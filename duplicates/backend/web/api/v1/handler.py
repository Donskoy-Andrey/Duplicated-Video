import contextlib
from http.client import HTTPException
from typing import Any

import msgpack
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_context import context
from starlette_context.errors import ContextDoesNotExistError

from consumer.handlers.handler import search_duplicate
from .router import router
from fastapi.responses import ORJSONResponse
from web.storage.db import get_db
from web.logger import logger
from web.storage.rabbit import channel_pool
from aio_pika.abc import DeliveryMode, ExchangeType
from aio_pika import Message, RobustChannel, Channel

from web.config.settings import settings

from .response_model import videoLinkResponseFront, videoLinkResponse
from .request_model import videoLinkRequest, videoRequestFront


class tmp(BaseModel):
    a: int
    b: str
    c: list[str]


@router.post('/puk')
async def first_post_handler(body: tmp, session: AsyncSession = Depends(get_db), ):
    # row = await session.execute(select(text('1')))
    # result, = row.one()
    #
    # row1 = await session.scalars(select(text('1')))
    # result1 = row1.one()
    # logger.info('Testim %s; %s', result, result1)
    #
    # await publish_message({'test': 'test'})

    return ORJSONResponse({'message': 'perduk!'}, status_code=200)


@router.post("/check-video-duplicate-front",
             response_model=videoLinkResponseFront,
             responses={
                 400: {"description": "Неверный запрос"},
                 500: {"description": "Ошибка сервера"}
             },
             tags=["API для проверки дубликатов видео на Фронтенд-Сервере"],
             summary="Проверка видео на дублирование")
async def check_video_duplicate_front(video: videoRequestFront):
    try:
        has_duplicate, potential_duplicate_uuid = await search_duplicate(video.link)

        if has_duplicate:
            return videoLinkResponseFront(
                is_duplicate=True,
                link_duplicate=f"https://s3.ritm.media/yappy-db-duplicates/{potential_duplicate_uuid}.mp4",
            )

        return videoLinkResponseFront(
            is_duplicate=False, link_duplicate="",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail="Неверный запрос")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@router.get('/puk')
async def first_handler(session: AsyncSession = Depends(get_db), ):
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
