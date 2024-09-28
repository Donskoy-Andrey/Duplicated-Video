import asyncio

import torch

from consumer.logger import logger
from .utils.utils import send_video_to_triton, search_in_faiss, video_url_to_tensor


async def handle_message(message: dict) -> None:
    logger.info('Received message: %s', message)


async def search_duplicate(message: dict):
    path_link = message['link']
    video_tensor_short, video_tensor_long = await asyncio.to_thread(video_url_to_tensor, path_link)
    query_embeddings = await asyncio.to_thread(send_video_to_triton, video_tensor_short, video_tensor_long)
    query_embeddings = torch.tensor(query_embeddings)
    potential_duplicate_uuid, has_duplicate = search_in_faiss(query_embeddings=query_embeddings)[0]
    return has_duplicate, potential_duplicate_uuid
