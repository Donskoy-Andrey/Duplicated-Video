import contextlib
from typing import Any

import msgpack
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_context import context
from starlette_context.errors import ContextDoesNotExistError

from .router import router
from fastapi.responses import ORJSONResponse
from web.storage.db import get_db
from web.logger import logger
from web.storage.rabbit import channel_pool
from aio_pika.abc import DeliveryMode, ExchangeType
from aio_pika import Message, RobustChannel, Channel

from web.config.settings import settings


class tmp(BaseModel):
    a: int
    b: str
    c: list[str]


@router.post('/puk')
async def first_post_handler(body: tmp, session: AsyncSession = Depends(get_db),):
    # row = await session.execute(select(text('1')))
    # result, = row.one()
    #
    # row1 = await session.scalars(select(text('1')))
    # result1 = row1.one()
    # logger.info('Testim %s; %s', result, result1)
    #
    # await publish_message({'test': 'test'})

    return ORJSONResponse({'message': 'perduk!'}, status_code=200)


@router.get('/puk')
async def first_handler(session: AsyncSession = Depends(get_db),):
    row = await session.execute(select(text('1')))
    result, = row.one()

    row1 = await session.scalars(select(text('1')))
    result1 = row1.one()
    logger.info('Testim %s; %s', result, result1)

    await publish_message({'test': 'test'})

    return ORJSONResponse({'message': 'perduk!'}, status_code=200)


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
