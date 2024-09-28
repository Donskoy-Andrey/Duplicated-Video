import asyncio

import torch
from fastapi import FastAPI, HTTPException

from .api.base import (
    videoLinkRequest,
    videoLinkResponse,
    videoLinkResponseFront,
    videoRequestFront,
)
from .api.utils import (
    search_in_faiss,
    send_video_to_triton,
    video_url_to_tensor,
)

app = FastAPI(
    title="Video Duplicate Checker API",
    version="1.0.0",
)


@app.post("/check-video-duplicate-front",
          response_model=videoLinkResponseFront,
          responses={
              400: {"description": "Неверный запрос"},
              500: {"description": "Ошибка сервера"}
          },
          tags=["API для проверки дубликатов видео на Фронтенд-Сервере"],
          summary="Проверка видео на дублирование")
async def check_video_duplicate_front(video: videoRequestFront):
    try:
        video_tensor_short, video_tensor_long = await asyncio.to_thread(
            video_url_to_tensor, video.link
        )
        query_embeddings = await asyncio.to_thread(
            send_video_to_triton, video_tensor_short, video_tensor_long
        )
        query_embeddings = torch.tensor(query_embeddings)
        potential_duplicate_uuid, has_duplicate = search_in_faiss(
            query_embeddings=query_embeddings, minimum_confidence_level=video.confidence_level,
        )[0]

        if has_duplicate:
            return videoLinkResponseFront(
                is_duplicate=True,
                link_duplicate=f"https://s3.ritm.media/yappy-db-duplicates/{potential_duplicate_uuid}.mp4",
            )
        return videoLinkResponseFront(
            is_duplicate=False, link_duplicate="",
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный запрос")
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@app.post("/check-video-duplicate",
          response_model=videoLinkResponse,
          responses={
              400: {"description": "Неверный запрос"},
              500: {"description": "Ошибка сервера"}
          },
          tags=["API для проверки дубликатов видео"],
          summary="Проверка видео на дублирование")
async def check_video_duplicate(videoLink: videoLinkRequest):
    try:
        video_tensor_short, video_tensor_long = await asyncio.to_thread(
            video_url_to_tensor, videoLink.link
        )
        query_embeddings = await asyncio.to_thread(
            send_video_to_triton, video_tensor_short, video_tensor_long
        )
        query_embeddings = torch.tensor(query_embeddings)
        potential_duplicate_uuid, has_duplicate = search_in_faiss(
            query_embeddings=query_embeddings
        )[0]

        if has_duplicate:
            return videoLinkResponse(
                is_duplicate=True, duplicate_for=potential_duplicate_uuid,
            )
        return videoLinkResponse(
            is_duplicate=False, duplicate_for="",
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный запрос")
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@app.post("/test_request")
async def test_request():
    # Examples
    # url = 'https://s3.ritm.media/yappy-db-duplicates/16a91af7-f3ac-4517-a051-5240b30f3217.mp4'
    # url = 'https://s3.ritm.media/yappy-db-duplicates/000be48d-c88c-4d48-8b7a-28430ac9b57d.mp4'

    # Duplicate
    # url = 'https://s3.ritm.media/yappy-db-duplicates/b5f191e6-42e0-43f5-8773-560643de17fb.mp4'

    # Original
    url = 'https://s3.ritm.media/yappy-db-duplicates/55635719-38d9-4adb-b455-4c852ed869e9.mp4'

    video_tensor_short, video_tensor_long = await asyncio.to_thread(
        video_url_to_tensor, url
    )
    query_embeddings = await asyncio.to_thread(
        send_video_to_triton, video_tensor_short, video_tensor_long
    )
    query_embeddings = torch.tensor(query_embeddings)
    output = search_in_faiss(query_embeddings=query_embeddings)

    print(output)
    print(query_embeddings.shape)
    return {"result": True}
