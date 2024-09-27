import cv2
import torch
import numpy as np

import cv2
import torch
import numpy as np


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
