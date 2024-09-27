import uuid

import requests
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, APIRouter

from fastapi.middleware.cors import CORSMiddleware

from duplicates.backend.api.check_video_duplicate import check_video_duplicate
from duplicates.backend.api.video_link_request import VideoLinkRequest
from duplicates.backend.api.video_link_response import VideoLinkResponse, VideoLinkResponseFront

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/check-video-duplicate",
          response_model=VideoLinkResponse,
          responses={
              400: {"description": "Неверный запрос"},
              500: {"description": "Ошибка сервера"}
          },
          tags=["API для проверки дубликатов видео"],
          summary="Проверка видео на дублирование")
async def task_api(link_request: VideoLinkRequest):
    return check_video_duplicate(link_request)


@app.post("/front_check-video-duplicate",
          response_model=VideoLinkResponseFront,
          responses={
              400: {"description": "Неверный запрос"},
              500: {"description": "Ошибка сервера"}
          },
          tags=["API для проверки дубликатов видео"],
          summary="Проверка видео на дублирование")
async def task_api(link_request: VideoLinkRequest):
    response = check_video_duplicate(link_request)
    if response.is_duplicate:
        url = f"https://s3.ritm.media/yappy-db-duplicates/{response.duplicate_for}.mp4"
        return VideoLinkResponseFront(is_duplicate=response.is_duplicate, duplicate_for=response.duplicate_for,
                                      link_duplicate=url)
    else:
        return VideoLinkResponseFront(is_duplicate = response.is_duplicate, duplicate_for = response.duplicate_for, link_duplicate = None)
