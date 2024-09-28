import uuid

import requests
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, APIRouter

from fastapi.middleware.cors import CORSMiddleware

from .api.check_video_duplicate import VideoDuplicateChecker
from .api.video_link_request import videoLinkRequest
from .api.video_link_response import videoLinkResponse, videoLinkResponseFront

app = FastAPI(
    title="Video Duplicate Checker API",
    version="1.0.0",
    description="API для проверки дубликатов видео"
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


duplicate_checker = VideoDuplicateChecker()


# @app.post("/check_duplicate", response_model=VideoLinkResponse)
# async def check_duplicate(request: VideoLinkRequest):
#     """
#     Эндпоинт для проверки дубликата видео.
#     """
#     return await duplicate_checker.check_video_duplicate(request)


@app.post("/check-video-duplicate",
          response_model=videoLinkResponse,
          responses={
              400: {"description": "Неверный запрос"},
              500: {"description": "Ошибка сервера"}
          },
          tags=["API для проверки дубликатов видео"],
          summary="Проверка видео на дублирование")
async def check_duplicate(body: videoLinkRequest):
    return await duplicate_checker.check_video_duplicate(body)


@app.post("/front-check-video-duplicate",
          response_model=videoLinkResponseFront,
          responses={
              400: {"description": "Неверный запрос"},
              500: {"description": "Ошибка сервера"}
          },
          tags=["API для проверки дубликатов видео"],
          summary="Проверка видео на дублирование")
async def task_api(link_request: videoLinkRequest):
    response = await duplicate_checker.check_video_duplicate(link_request)
    if response.is_duplicate:
        url = f"https://s3.ritm.media/yappy-db-duplicates/{response.duplicate_for}.mp4"
        return videoLinkResponseFront(is_duplicate=response.is_duplicate, duplicate_for=response.duplicate_for,
                                      link_duplicate=url)
    else:
        return videoLinkResponseFront(is_duplicate=response.is_duplicate, duplicate_for=response.duplicate_for,
                                      link_duplicate=None)
