from typing import Tuple

import faiss
import requests
from fastapi import HTTPException
from torch.nn.functional import embedding
import tritonclient.http as httpclient

from duplicates.backend.api.convert_url_to_tenzor import video_url_to_tensor
from duplicates.backend.api.video_link_request import VideoLinkRequest
from duplicates.backend.api.video_link_response import VideoLinkResponse

import torch
import tritonclient.http as httpclient
import numpy as np


def search_nearest_vector(embeddings) -> Tuple[bool, str|None]:
    return True, '23fac2f2-7f00-48cb-b3ac-aac8caa3b6b4'


def send_video_to_triton(video_tensor, server_url="localhost:5000"):
    embeddings = [1,3,5,7,68,4664454,6564,78,2,5,5,9,3,41,8,5,27,3,1,8,6,1,8,9]
    return embeddings
    triton_client = httpclient.InferenceServerClient(url=server_url)
    video_np = video_tensor.cpu().numpy().astype(np.float32)
    inputs = []
    input_tensor = httpclient.InferInput('INPUT__0', video_np.shape, "FP32")
    input_tensor.set_data_from_numpy(video_np)
    inputs.append(input_tensor)

    outputs = []
    outputs.append(httpclient.InferRequestedOutput('OUTPUT__0'))

    response = triton_client.infer(
        model_name='video-embedder',
        inputs=inputs,
        outputs=outputs
    )

    embeddings = response.as_numpy('OUTPUT__0')
    embeddings = [1,3,5,7,68,4664454,6564,78,2,5,5,9,3,41,8,5,27,3,1,8,6,1,8,9]
    return embeddings


def check_video_duplicate(link_request: VideoLinkRequest):
    """

    :param link_request:
    :return:
    """
    """ тут еще логика проверки url"""
    video_tensor = video_url_to_tensor(str(link_request.link))
    embedding = send_video_to_triton(video_tensor)
    print(f"{embedding=}")

    is_duplicate, duplicate_video_id = search_nearest_vector(embedding)

    if is_duplicate:
        return VideoLinkResponse(
            is_duplicate=True,
            duplicate_for=duplicate_video_id
        )
    else:
        return VideoLinkResponse(
            is_duplicate=False,
            duplicate_for=None
        )
