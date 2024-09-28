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
