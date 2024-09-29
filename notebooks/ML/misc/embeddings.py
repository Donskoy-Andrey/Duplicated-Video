import numpy

import torch
import torchvision
import pytorchvideo

from torchvision.transforms import Compose, Lambda
from pytorchvideo.data.encoded_video import EncodedVideo

from pytorchvideo.transforms import UniformTemporalSubsample

from tqdm import trange

from collections import defaultdict


class VideoEncoder(torch.nn.Module):
    """
    Video encoder
    """

    def __init__(self, backbone: torch.nn.Module, head: torch.nn.Module=torch.nn.Identity, transform: torch.nn.Module=torch.nn.Identity) -> None:
        super().__init__()

        self.transform = transform
        self.backbone = backbone
        self.head = head

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.transform(x)
        x = self.backbone(x)
        x = self.head(x)

        return x


class InfoNCELoss(torch.nn.Module):
    """
    Noise-Contrastive Estimation variational lower bound for
    the mutual information.

    References
    ----------
    .. [1] Oord A., Li Y. and Vinyals O. "Representation Learning with
           Contrastive Predictive Coding". arXiv:1807.03748
    """
    
    def __init__(self, temperature: float=1.0e4):
        super().__init__()

        self.temperature = temperature

    def forward(self, T_positive: torch.tensor, T_negative: torch.tensor) -> torch.tensor:
        """
        Forward pass.
        
        Parameters
        ----------
        T_product : torch.tensor
            Critic network value on all pairs of samples from the batch.
        """

        #batch_size = math.isqrt(T_negative.shape[0])
        #T_negative = T_negative.view((batch_size, batch_size))

        return torch.mean(torch.logsumexp((T_negative - T_positive[:,None]) / self.temperature, dim=-1))# - math.log(batch_size)


#def encode_frames(encoder: torch.nn.Module, frames: torch.Tensor, n_frames: int=16, n_pathces: int=32) -> tuple[torch.Tensor, torch.Tensor]:


class ContrastiveDuplicatesDataset(torch.utils.data.Dataset):
    def __init__(self, objects, positive_indices, n_negatives: int=64) -> None:
        self.objects = objects
        self.positive_indices = positive_indices
        self.n_negatives = n_negatives

    def __len__(self) -> int:
        return len(self.positive_indices)

    def __getitem__(self, index):
        positive_pair = self.positive_indices[index]
        
        positive_x = self.objects[positive_pair[0]]
        positive_y = self.objects[positive_pair[1]]

        negative_indices = torch.randperm(self.objects.shape[0])[:self.n_negatives]
        negative = torch.index_select(self.objects, 0, negative_indices)

        return positive_x, positive_y, negative


def train_head(encoder: torch.nn.Module,
               train_dataloader: torch.utils.data.DataLoader,
               test_dataloader: torch.utils.data.DataLoader,
               device: str, n_epochs: int,
               optimizer_factory=lambda parameters: torch.optim.Adam(parameters, lr=1.0e-3),
               loss_factory: torch.nn.Module=InfoNCELoss) -> dict[list]:
    
    optimizer = optimizer_factory(encoder.head.parameters())
    loss = loss_factory()

    history = defaultdict(list)

    for epoch in trange(1, n_epochs+1):
        total_loss_value = 0.0
        total_batches = 0
        for batch in train_dataloader:
            optimizer.zero_grad()
            
            positive_x, positive_y, negative = batch
            dim = positive_x.shape[-1]

            # Positive.
            positive_x = torch.nn.functional.normalize(encoder.head(positive_x.to(device)))
            positive_y = torch.nn.functional.normalize(encoder.head(positive_y.to(device)))
            T_positive = torch.sum(positive_x * positive_y, axis=-1)

            # Negative.
            negative = torch.nn.functional.normalize(encoder.head(negative.to(device).reshape(-1, dim)))
            T_negative = torch.sum(negative.reshape(positive_x.shape[0], -1, positive_x.shape[-1]) * positive_x[:,None,:], axis=-1)

            loss_value = loss(T_positive, T_negative)
            loss_value.backward()

            optimizer.step()

            total_loss_value += loss_value.detach().cpu().item()
            total_batches += 1

        history["train_loss"].append(total_loss_value / total_batches)

    return history