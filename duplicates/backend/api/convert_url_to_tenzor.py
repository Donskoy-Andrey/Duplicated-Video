import cv2
import tritonclient.grpc as grpcclient
import numpy as np

from fastapi import FastAPI

import requests
from io import BytesIO
from pytorchvideo.data.encoded_video import select_video_class

# def video_url_to_tensor(
#         url: str = 'https://s3.ritm.media/yappy-db-duplicates/16a91af7-f3ac-4517-a051-5240b30f3217.mp4'
# ) -> list[torch.Tensor, torch.Tensor]:
#     cap = cv2.VideoCapture(url)
#     total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#     frame_indices_long = np.linspace(0, total_frames - 1, 32, dtype=int)
#     frame_indices_short = np.linspace(0, total_frames - 1, 8, dtype=int)
#
#     frames_long, frames_short = [], []
#     for i in range(total_frames):
#         ret, frame = cap.read()
#         if not ret:
#             break
#
#         if i in frame_indices_long:
#             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             frame_resized = cv2.resize(frame_rgb, (256, 256), interpolation=cv2.INTER_AREA)
#             frame_tensor = torch.from_numpy(frame_resized).permute(2, 0, 1)  # (H, W, C) -> (C, H, W)
#             frames_long.append(frame_tensor)
#
#         if i in frame_indices_short:
#             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             frame_resized = cv2.resize(frame_rgb, (256, 256), interpolation=cv2.INTER_AREA)
#             frame_tensor = torch.from_numpy(frame_resized).permute(2, 0, 1)  # (H, W, C) -> (C, H, W)
#             frames_short.append(frame_tensor)
#
#     cap.release()
#
#     video_tensor_long = torch.stack(frames_long)
#     video_tensor_short = torch.stack(frames_short)
#     video_tensor_long.shape == [32, 3, 256, 256]
#     video_tensor_short.shape == [8, 3, 256, 256]
#
#     return video_tensor_long, video_tensor_short

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
        print('ТУТ')
        super().__init__()
        print('Тут0')

        self.side_size = side_size
        self.mean = mean
        self.std = std
        self.crop_size = crop_size
        self.num_frames = num_frames
        self.sampling_rate = sampling_rate
        self.frames_per_second = frames_per_second
        self.alpha = alpha
        print('Тут1')

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
        print('Тут2')

    @property
    def clip_duration(self) -> float:
        return (self.num_frames * self.sampling_rate) / self.frames_per_second

    def forward(self, frames: torch.Tensor):
        return self.transform(frames)
