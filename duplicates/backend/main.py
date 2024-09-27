import cv2
import torch
import tritonclient.grpc as grpcclient
import numpy as np

from fastapi import FastAPI

from .task_api import check_video_duplicate, VideoLinkRequestBody, VideoLinkResponse

app = FastAPI()


@app.post("/check-video-duplicate",
          response_model=VideoLinkResponse,
          responses={
              400: {"description": "Неверный запрос"},
              500: {"description": "Ошибка сервера"}
          },
          tags=["API для проверки дубликатов видео"],
          summary="Проверка видео на дублирование")
async def task_api(body: VideoLinkRequestBody):
    return check_video_duplicate(body)


def video_url_to_tensor(
        url: str = 'https://s3.ritm.media/yappy-db-duplicates/16a91af7-f3ac-4517-a051-5240b30f3217.mp4'
) -> list[torch.Tensor, torch.Tensor]:
    cap = cv2.VideoCapture(url)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indices_long = np.linspace(0, total_frames - 1, 32, dtype=int)
    frame_indices_short = np.linspace(0, total_frames - 1, 8, dtype=int)

    frames_long, frames_short = [], []
    for i in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break

        if i in frame_indices_long:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (256, 256), interpolation=cv2.INTER_AREA)
            frame_tensor = torch.from_numpy(frame_resized).permute(2, 0, 1)  # (H, W, C) -> (C, H, W)
            frames_long.append(frame_tensor)

        if i in frame_indices_short:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (256, 256), interpolation=cv2.INTER_AREA)
            frame_tensor = torch.from_numpy(frame_resized).permute(2, 0, 1)  # (H, W, C) -> (C, H, W)
            frames_short.append(frame_tensor)

    cap.release()

    video_tensor_long = torch.stack(frames_long)
    video_tensor_short = torch.stack(frames_short)
    video_tensor_long.shape == [32, 3, 256, 256]
    video_tensor_short.shape == [8, 3, 256, 256]

    return video_tensor_long, video_tensor_short


def send_video_to_triton(video_tensor_long, video_tensor_short, server_url="triton:8004"):
    triton_client = grpcclient.InferenceServerClient(url=server_url)

    # Преобразуем тензоры в numpy
    video_tensor_long = video_tensor_long.unsqueeze(0)
    video_tensor_long_np = video_tensor_long.cpu().numpy().astype(np.float32)

    video_tensor_short = video_tensor_short.unsqueeze(0)
    video_tensor_short_np = video_tensor_short.cpu().numpy().astype(np.float32)

    # Создаем входные тензоры
    inputs = []
    input_tensor_long = grpcclient.InferInput('input__0', video_tensor_long.shape, "FP32")
    input_tensor_long.set_data_from_numpy(video_tensor_long_np)

    input_tensor_short = grpcclient.InferInput('input__1', video_tensor_short.shape, "FP32")
    input_tensor_short.set_data_from_numpy(video_tensor_short_np)

    inputs.append(input_tensor_long)
    inputs.append(input_tensor_short)

    outputs = []
    outputs.append(grpcclient.InferRequestedOutput('output__0'))

    response = triton_client.infer(
        model_name='video-embedder',
        inputs=inputs,
        outputs=outputs
    )

    embeddings = response.as_numpy('output__0')

    return embeddings


@app.post("/test_request")
async def test_request():
    tensor_ = video_url_to_tensor()
    # print(tensor_)
    send_video_to_triton(*tensor_)
    return {"result": 123}
