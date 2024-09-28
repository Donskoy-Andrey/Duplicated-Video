import cv2
import tritonclient.http as httpclient
import numpy as np

from fastapi import FastAPI
import torch

from torchvision.transforms import Compose, Lambda
from torchvision.transforms._transforms_video import (
    CenterCropVideo,
    NormalizeVideo,
)
from pytorchvideo.transforms import (
    ApplyTransformToKey,
    ShortSideScale,
    UniformTemporalSubsample,
)
from .task_api import check_video_duplicate, VideoLinkRequestBody, VideoLinkResponse
import requests
from io import BytesIO
from pytorchvideo.data.encoded_video import select_video_class


app = FastAPI()


class PackPathway(torch.nn.Module):
    """
    Transform for converting video frames as a list of tensors.
    """

    def __init__(self, alpha: int = 4):
        super().__init__()

        self.alpha = alpha

    def forward(self, frames: torch.Tensor) -> list[torch.Tensor]:
        fast_pathway = frames

        # Perform temporal sampling from the fast pathway.
        slow_pathway = torch.index_select(
            frames,
            1,
            torch.linspace(
                0, frames.shape[1] - 1, frames.shape[1] // self.alpha
            ).long(),
        )

        return [slow_pathway, fast_pathway]


class VideoTransform(torch.nn.Module):
    def __init__(
            self,
            side_size: int = 256,
            mean: list = [0.45, 0.45, 0.45],
            std: list = [0.225, 0.225, 0.225],
            crop_size: int = 256,
            num_frames: int = 32,
            sampling_rate: int = 2,
            frames_per_second: int = 30,
            alpha: int = 4
    ) -> None:
        super().__init__()

        self.side_size = side_size
        self.mean = mean
        self.std = std
        self.crop_size = crop_size
        self.num_frames = num_frames
        self.sampling_rate = sampling_rate
        self.frames_per_second = frames_per_second
        self.alpha = alpha

        # self.clip_duration = (self.num_frames * self.sampling_rate) / self.frames_per_second

        self.transform = ApplyTransformToKey(
            key="video",
            transform=Compose(
                [
                    UniformTemporalSubsample(self.num_frames),
                    Lambda(lambda x: x / 255.0),
                    NormalizeVideo(self.mean, self.std),
                    ShortSideScale(
                        size=self.side_size
                    ),
                    CenterCropVideo(self.crop_size),
                    PackPathway(self.alpha),
                ]
            )
        )

    @property
    def clip_duration(self) -> float:
        return (self.num_frames * self.sampling_rate) / self.frames_per_second

    def forward(self, frames: torch.Tensor):
        return self.transform(frames)


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


def video_url_to_tensor(url: str) -> list[torch.Tensor, torch.Tensor]:
    """
    SOME TRASH
    DO NOT DELETE

    response = requests.get(url)
    video_file = BytesIO(response.content)

    video_cls = select_video_class("pyav")

    video = video_cls(
        file=video_file,
        video_name="downloaded",
        decode_video=True,
        decode_audio=True,
    )

    start_sec = 0
    end_sec = int(video.duration)
    try:
        video_data = video.get_clip(start_sec=start_sec, end_sec=end_sec)
    except Exception as e:
        print(e)
        print("hui")

    # video._video, video._audio = video._pyav_decode_video(start_sec, end_sec)
    # video_data = {
    #     "video": video._video,
    #     "audio": video._audio,
    # }
    print(video_data)
    print("*"*40)
    video_transform = VideoTransform()
    video_data = video_transform(video_data)
    video_tensor_short, video_tensor_long = video_data["video"]

    video_data = {
        "video": video._video,
        "audio": video._audio,
    }
    """
    cap = cv2.VideoCapture(url)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frames = []
    for i in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_tensor = torch.from_numpy(frame_rgb).permute(2, 0, 1)  # (H, W, C) -> (C, H, W)
        frames.append(frame_tensor)

    cap.release()

    frames = torch.stack(frames).permute(1, 0, 2, 3)
    transform = VideoTransform()
    video_tensor_short, video_tensor_long = transform({"video": frames})["video"]

    # if list(video_tensor_short.shape) != [3, 8, 256, 256]:
    #     video_tensor_short = torch.rand(3, 8, 256, 256)
    #
    # if list(video_tensor_long.shape) != [3, 32, 256, 256]:
    #     video_tensor_long = torch.rand(3, 8, 256, 256)

    return video_tensor_short, video_tensor_long


def send_video_to_triton(video_tensor_short, video_tensor_long, server_url="triton:8004"):
    triton_client = httpclient.InferenceServerClient(url=server_url)

    if video_tensor_long.dim() != 5:
        video_tensor_long = video_tensor_long.unsqueeze(0)
    video_tensor_long_np = video_tensor_long.cpu().numpy().astype(np.float32)

    if video_tensor_short.dim() != 5:
        video_tensor_short = video_tensor_short.unsqueeze(0)
    video_tensor_short_np = video_tensor_short.cpu().numpy().astype(np.float32)

    input_tensor_short = httpclient.InferInput('input__0', video_tensor_short.shape, "FP32")
    input_tensor_short.set_data_from_numpy(video_tensor_short_np)

    input_tensor_long = httpclient.InferInput('input__1', video_tensor_long.shape, "FP32")
    input_tensor_long.set_data_from_numpy(video_tensor_long_np)

    inputs = [
        input_tensor_short,
        input_tensor_long,
    ]

    outputs = [
        httpclient.InferRequestedOutput('output__0')
    ]

    response = triton_client.infer(
        model_name='video-embedder',
        inputs=inputs,
        outputs=outputs
    )

    embeddings = response.as_numpy('output__0')

    return embeddings


@app.post("/test_request")
async def test_request():
    # url = 'https://s3.ritm.media/yappy-db-duplicates/16a91af7-f3ac-4517-a051-5240b30f3217.mp4'
    url = 'https://s3.ritm.media/yappy-db-duplicates/000be48d-c88c-4d48-8b7a-28430ac9b57d.mp4'
    video_tensor_short, video_tensor_long = video_url_to_tensor(url=url)
    embeddings = send_video_to_triton(video_tensor_short, video_tensor_long)
    embeddings = embeddings.tolist()
    return {"result": embeddings}
