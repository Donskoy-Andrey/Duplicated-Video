import tempfile

import cv2
import faiss
import numpy as np
import pandas as pd
import torch
import tritonclient.grpc as grpcclient
from consumer.handlers.utils.video_transform import VideoTransform


def video_url_to_tensor(url: str) -> list[torch.Tensor, torch.Tensor]:
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
        minimum_confidence_level: float = 0.97,
        top_k: int = 3,
):
    assert query_embeddings.shape[1] == 400  # [batch, 400]

    uuid_path = '/data/embeddings_uuid.csv'
    embeddings_uuid = pd.read_csv(uuid_path)
    # embeddings_datetimes = embeddings_uuid["created"].to_numpy().astype(np.datetime64)
    embeddings_uuid = embeddings_uuid["uuid"].to_numpy()

    id_to_uuid = embeddings_uuid
    # id_to_datetime = embeddings_datetimes
    # uuid_to_id = {value: index for index, value in enumerate(id_to_uuid)}

    uuid_embeddings_path = "/data/embeddings.pt"
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