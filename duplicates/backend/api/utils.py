import asyncio
import tempfile
from http.client import HTTPException
from typing import Union

import cv2

import numpy as np
import torch
import tritonclient.grpc as grpcclient

from pytorchvideo.transforms import (
    ApplyTransformToKey,
    ShortSideScale,
    UniformTemporalSubsample,
)

import pandas as pd
import faiss

from .base import videoLinkResponse
from torchvision.transforms import Compose, Lambda
from torchvision.transforms._transforms_video import (
    CenterCropVideo,
    NormalizeVideo,
)


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
    frame_indices_long = np.linspace(0, total_frames - 1, 32, dtype=int)

    frames_long, frames_short = [], []
    for i in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break

        if i in frame_indices_long:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # frame_resized = cv2.resize(frame_rgb, (256, 256), interpolation=cv2.INTER_AREA)
            frame_tensor = torch.from_numpy(frame_rgb).permute(2, 0, 1)  # (H, W, C) -> (C, H, W)
            frames_long.append(frame_tensor)

    cap.release()

    frames = torch.stack(frames_long).permute(1, 0, 2, 3)
    transform = VideoTransform()
    video_tensor_short, video_tensor_long = transform({"video": frames})["video"]

    # if list(video_tensor_short.shape) != [3, 8, 256, 256]:
    #     video_tensor_short = torch.rand(3, 8, 256, 256)
    #
    # if list(video_tensor_long.shape) != [3, 32, 256, 256]:
    #     video_tensor_long = torch.rand(3, 8, 256, 256)

    return video_tensor_short, video_tensor_long


def send_video_to_triton(video_tensor_short, video_tensor_long, server_url="triton:8004"):
    triton_client = grpcclient.InferenceServerClient(url=server_url)

    if video_tensor_long.dim() != 5:
        video_tensor_long = video_tensor_long.unsqueeze(0)
    video_tensor_long_np = video_tensor_long.cpu().numpy().astype(np.float32)

    if video_tensor_short.dim() != 5:
        video_tensor_short = video_tensor_short.unsqueeze(0)
    video_tensor_short_np = video_tensor_short.cpu().numpy().astype(np.float32)

    input_tensor_short = grpcclient.InferInput('input__0', video_tensor_short.shape, "FP32")
    input_tensor_short.set_data_from_numpy(video_tensor_short_np)

    input_tensor_long = grpcclient.InferInput('input__1', video_tensor_long.shape, "FP32")
    input_tensor_long.set_data_from_numpy(video_tensor_long_np)

    inputs = [
        input_tensor_short,
        input_tensor_long,
    ]

    outputs = [
        grpcclient.InferRequestedOutput('output__0')
    ]

    response = triton_client.infer(
        model_name='video-embedder',
        inputs=inputs,
        outputs=outputs
    )

    embeddings = response.as_numpy('output__0')

    return embeddings


def search_in_faiss(
        query_embeddings: torch.Tensor,
        # query_datetimes: np.ndarray,
        minimum_confidence_level: float = 0.95,
        top_k: int = 3,
):
    assert query_embeddings.shape[1] == 400  # [batch, 400]

    uuid_path = './embeddings_uuid.csv'
    embeddings_uuid = pd.read_csv(uuid_path)
    # embeddings_datetimes = embeddings_uuid["created"].to_numpy().astype(np.datetime64)
    embeddings_uuid = embeddings_uuid["uuid"].to_numpy()

    id_to_uuid = embeddings_uuid
    # id_to_datetime = embeddings_datetimes
    # uuid_to_id = {value: index for index, value in enumerate(id_to_uuid)}

    uuid_embeddings_path = "./embeddings.pt"
    uuid_embeddings = torch.load(uuid_embeddings_path, weights_only=True)

    # Create Faiss index
    faiss.normalize_L2(uuid_embeddings.cpu().numpy())
    index = faiss.IndexFlatIP(uuid_embeddings.shape[-1])
    index.add(uuid_embeddings)

    # Normalize query
    l2_norm = np.linalg.norm(query_embeddings, axis=1, keepdims=True)
    query_embeddings = query_embeddings / l2_norm

    # Find closest
    distances, indices = index.search(query_embeddings, top_k)

    id_to_choose = 0
    y_score = np.clip(distances[:, id_to_choose], 0.0, 1.0)
    y_score_bool = y_score > minimum_confidence_level
    # datetime_bool = query_datetimes < id_to_datetime[indices[:, 0]]

    output = tuple(zip(
        id_to_uuid[indices[:, id_to_choose]],  # Closest neighbour: 0e6519b6-8d41-4d0f-8d3b-7c9ab1f5aab6
        # y_score_bool * datetime_bool,     # Neighbour found or not
        y_score_bool,
    ))
    """
    Example of output for batch_size = 2
    (('000be48d-c88c-4d48-8b7a-28430ac9b57d', False),
     ('000be48d-c88c-4d48-8b7a-28430ac9b57d', True))
    """
    return output


def video_bytes_to_tensor(bytes_data):
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp4") as temp_video:
        temp_video.write(bytes_data)
        temp_video.flush()
    return video_url_to_tensor(temp_video.name)


async def search_duplicate(path_link: Union[str, bytes]):
        print(f"{len(path_link)=}")
        video_tensor_short, video_tensor_long = await asyncio.to_thread(video_url_to_tensor, path_link)
        print('video_tensor_short',len(video_tensor_short))
        query_embeddings = await asyncio.to_thread(send_video_to_triton, video_tensor_short, video_tensor_long)
        query_embeddings = torch.tensor(query_embeddings)
        potential_duplicate_uuid, has_duplicate = search_in_faiss(query_embeddings=query_embeddings)[0]
        return has_duplicate, potential_duplicate_uuid



