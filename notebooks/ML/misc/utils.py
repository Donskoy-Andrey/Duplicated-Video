import torch
import torchvision
import pytorchvideo

from torchvision.transforms import Compose, Lambda
from torchvision.transforms._transforms_video import (
    CenterCropVideo,
    NormalizeVideo,
)
from pytorchvideo.transforms import (
    ApplyTransformToKey,
    ShortSideScale,
    UniformTemporalSubsample,
    UniformCropVideo
)

from pytorchvideo.data.encoded_video import EncodedVideo

#from itertools import batched
from itertools import islice

from pathlib import Path


def batched(iterable, n):
      "Batch data into lists of length n. The last batch may be shorter."
      # batched('ABCDEFG', 3) --> ABC DEF G
      if n < 1:
          raise ValueError('n must be >= 1')
      it = iter(iterable)
      while (batch := list(islice(it, n))):
          yield batch


def walk_directory(path: Path) -> list[str]:
    filenames = []

    for file_path in path.iterdir():
        if file_path.is_file():
            filenames.append(file_path.name)

    return filenames


def encode_videos(path: Path, filenames: str,
                  model, video_transform, device,
                  duration_cap: int=600,
                  batch_size: int=32):
    was_in_training = model.training
    model.eval()

    embeddings = []
    durations = []

    with torch.no_grad():
        for filenames_batch in batched(filenames, batch_size):
            inputs_batch = None
            for filename in filenames_batch:
                file_path = path / filename
                video = EncodedVideo.from_path(file_path)
    
                start_sec = 0
                #end_sec = start_sec + video_transform.clip_duration
                end_sec = min(duration_cap, video.duration)
                durations.append(video.duration)
                
                video_data = video.get_clip(start_sec=start_sec, end_sec=end_sec)
                video_data = video_transform(video_data)
    
                inputs = video_data["video"]
                inputs = [tensor.to(device)[None, ...] for tensor in inputs]

                if inputs_batch is None:
                    inputs_batch = [[tensor] for tensor in inputs]
                else:
                    for inputs_batch_part, inputs_part in zip(inputs_batch, inputs):
                        inputs_batch_part.append(inputs_part)
    
            
            inputs_batch = [torch.cat(inputs_batch_part, dim=0) for inputs_batch_part in inputs_batch]
            embedding = model(inputs_batch)

            del inputs_batch
            
            embeddings.append(embedding.detach().cpu())
        
        embeddings = torch.cat(embeddings, dim=0)
            
    model.train(was_in_training)

    return embeddings, durations


class PackPathway(torch.nn.Module):
    """
    Transform for converting video frames as a list of tensors.
    """
    def __init__(self, alpha: int=4):
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
            side_size: int=256,
            mean: list=[0.45, 0.45, 0.45],
            std: list = [0.225, 0.225, 0.225],
            crop_size: int=256,
            num_frames: int=32,
            sampling_rate: int=2,
            frames_per_second: int=30,
            alpha: int=4
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

        #self.clip_duration = (self.num_frames * self.sampling_rate) / self.frames_per_second
        
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