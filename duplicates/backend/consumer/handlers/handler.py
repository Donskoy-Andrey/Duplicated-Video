import asyncio

import torch
from sqlalchemy.ext.asyncio import AsyncSession

from consumer.logger import logger
from consumer.storage.db import get_db
from sqlalchemy import insert, select, update
from web.storage.db import Jobs, async_session
from consumer.handlers.utils.utils import send_video_to_triton, search_in_faiss, video_url_to_tensor


async def search_duplicate(message: dict) -> None:
    path_link = message['body']['data']['link']
    conf_level = message['body']['data']['confidence_level']
    video_tensor_short, video_tensor_long = await asyncio.to_thread(video_url_to_tensor, path_link)
    query_embeddings = await asyncio.to_thread(send_video_to_triton, video_tensor_short, video_tensor_long)
    query_embeddings = torch.tensor(query_embeddings)
    potential_duplicate_uuid, has_duplicate = search_in_faiss(query_embeddings=query_embeddings,
                                                              minimum_confidence_level=conf_level)[0]

    async with async_session() as session:
        logger.info(f"Start work with queued job")
        row = await session.execute(select(Jobs).filter_by(uid=message["uid"]))
        job = row.scalar_one()
        session.refresh(job)
        job.is_processed = True # сюда результат работы
        job.is_duplicate = has_duplicate
        job.duplicate_for = potential_duplicate_uuid
        if has_duplicate:
            job.duplicate_link = f"https://s3.ritm.media/yappy-db-duplicates/{potential_duplicate_uuid}.mp4"
        else:
            job.duplicate_link = ""
        await session.commit()
        row_check_obj = await session.execute(select(Jobs.is_processed).where(Jobs.uid == message["uid"]))
        row_check = row_check_obj.scalar_one()
        session.refresh(row_check)

        logger.info(f"Finish work with queued job; Processed: {row_check}")

