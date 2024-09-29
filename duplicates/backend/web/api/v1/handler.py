import contextlib

from typing import Any
from uuid import uuid4
import tempfile
import msgpack
import sqlalchemy
from fastapi import Depends, UploadFile, File, Form, HTTPException
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

from web.api.v1.response_model import videoLinkResponseFront, ResultResponse
from web.api.v1.request_model import videoRequestFront, ResultRequest


@router.post('/upload-link',
             response_model=videoLinkResponseFront,
             responses={
                 400: {"description": "Неверный запрос"},
                 500: {"description": "Ошибка сервера"}
             },
             tags=["API для проверки дубликатов видео на Фронтенд-Сервере"],
             summary="Проверка видео на дублирование")
async def upload_link(video: videoRequestFront, session: AsyncSession = Depends(get_db),):
    current_id = str(uuid4())
    db_job = Jobs(uid=current_id, is_processed=False)
    session.add(db_job)
    await session.commit()

    await publish_message({'uid': current_id,
                           'body': {'type':
                                    'front_link',
                                    'data':
                                        {"link": video.link, "confidence_level": video.confidence_level}}
                           })

    return JSONResponse({'uid': current_id}, status_code=200)


@router.post('/upload-file',
             response_model=videoLinkResponseFront,
             responses={
                 400: {"description": "Неверный запрос"},
                 500: {"description": "Ошибка сервера"}
             },
             tags=["API для проверки дубликатов видео на Фронтенд-Сервере"],
             summary="Проверка видео на дублирование")
async def upload_file(file: UploadFile = File(...), confidenceLevel: float = Form(default=0.95), session: AsyncSession = Depends(get_db),):
    if file.content_type != "video/mp4":
        raise HTTPException(status_code=400, detail="Допускаются только файлы MP4.")

    try:
        video_bytes = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(video_bytes)
            temp_video.flush()
            temp_video.close()


    except ValueError as e:
        raise HTTPException(status_code=400, detail="Неверный запрос")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка сервера")

    current_id = str(uuid4())
    db_job = Jobs(uid=current_id, is_processed=False)
    session.add(db_job)
    await session.commit()

    await publish_message({'uid': current_id,
                           'body': {'type':
                                    'front_file',
                                    'data':
                                        {"link": tempfile.name, "confidence_level": float(confidenceLevel)}}
                           })

    return JSONResponse({'uid': current_id}, status_code=200)


@router.post('/get-result', response_model=ResultResponse)
async def get_result(body: ResultRequest, session: AsyncSession = Depends(get_db),):
    uid = body.uid

    job = await session.scalars(select(Jobs).filter_by(uid=uid))
    try:
        row = job.one()
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=400, detail="Wrong uid")

    session.refresh(row)

    if row.is_processed:
        res = {
               "is_duplicate": row.is_duplicate,
               "duplicate_link": row.duplicate_link
        }
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
