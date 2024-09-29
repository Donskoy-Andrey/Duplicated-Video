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


def walk_directory(path: Path, max_size: int=1024*1024) -> list[str]:
    filenames = []

    for file_path in path.iterdir():
        if file_path.is_file():
            if file_path.stat().st_size < max_size:
                filenames.append(file_path.name)

    return filenames


def encode_videos(path: Path, filenames: str,
                  model, video_transform, frames_transform, device,
                  duration_cap: int=600,
                  batch_size: int=32):
    was_in_training = model.training
    model.eval()

    embeddings = []
    durations = []

    with torch.no_grad():
        for filenames_batch in batched(filenames, batch_size):
            inputs_batch = []
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
                inputs = inputs.to(device).swapaxes(0,1)[None, ...]
                inputs = torchvision.models.video.MViT_V1_B_Weights.KINETICS400_V1.transforms()(inputs)

                inputs_batch.append(inputs)
            
            
            inputs_batch = torch.cat(inputs_batch, dim=0)
            embedding = model(inputs_batch)

            del inputs_batch
            
            embeddings.append(embedding.detach().cpu())
        
        embeddings = torch.cat(embeddings, dim=0)
            
    model.train(was_in_training)

    return embeddings, durations


class VideoTransform(torch.nn.Module):
    def __init__(
            self,
            side_size: int=256,
            num_frames: int=16,
        ) -> None:

        super().__init__()

        self.side_size = side_size
        self.num_frames = num_frames

        #self.clip_duration = (self.num_frames * self.sampling_rate) / self.frames_per_second
        
        self.transform = ApplyTransformToKey(
            key="video",
            transform=Compose(
                [
                    UniformTemporalSubsample(self.num_frames),
                    #ShortSideScale(
                    #    size=self.side_size
                    #),
                ]
            )
        )
    
    def forward(self, frames: torch.Tensor):
        return self.transform(frames)