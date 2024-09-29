import contextlib
from typing import Any
from uuid import uuid4

import msgpack
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from starlette_context import context
from starlette_context.errors import ContextDoesNotExistError

from .router import router
from fastapi.responses import ORJSONResponse
from web.storage.db import get_db, async_session
from web.logger import logger
from web.storage.rabbit import channel_pool
from aio_pika.abc import DeliveryMode, ExchangeType
from aio_pika import Message, RobustChannel, Channel

from web.config.settings import settings
from web.storage.db import Jobs

class tmp(BaseModel):
    a: int
    b: str
    c: list[str]


@router.post('/check-video-duplicate')
async def main_handler(body: tmp, session: AsyncSession = Depends(get_db),):
    current_id = str(uuid4())
    db_job = Jobs(uid=current_id, is_processed=False)
    session.add(db_job)
    await session.commit()

    await publish_message({'uid': current_id, 'body': {'type': 'example', 'data': 123}})

    return JSONResponse({'uid': current_id}, status_code=200)


class tmp2(BaseModel):
    uid: str


@router.post('/get-result')
async def get_result(body: tmp2, session: AsyncSession = Depends(get_db),):
    uid = body.uid

    job = await session.scalars(select(Jobs).filter_by(uid=uid))
    row = job.one()
    session.refresh(row)

    if row.is_processed:
        res = {"is_processed": row.is_processed, "is_duplicate": row.is_duplicate, "duplicate_for": row.duplicate_for}
        return JSONResponse(content=res, status_code=200)
    else:
        return JSONResponse(content={}, status_code=200)


async def publish_message(body: dict[str, Any]) -> None:
    logger.info('Sending message: %s', body)
    async with channel_pool.acquire() as channel:  # type: Channel
        exchange = await channel.declare_exchange(
            settings.EXCHANGE,
            type=ExchangeType.TOPIC,
            durable=True,
        )

        message_info = {
            'body': msgpack.packb(body),
            'delivery_mode': DeliveryMode.PERSISTENT,
        }

        with contextlib.suppress(ContextDoesNotExistError):
            if correlation_id := context.get('X-Correlation-ID'):
                message_info['correlation_id'] = correlation_id

        await exchange.publish(
            Message(**message_info),
            routing_key=settings.QUEUE,
        )
