import os
import shutil
import uuid
from typing import Optional

from fastapi import FastAPI
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

UPLOAD_DIR = "../../data/uploaded_videos"


@app.get("/")
async def root():
    return {"message": "Hello World"}


class UploadVideoResponse(BaseModel):
    is_duplicate: bool = Field(
        ...,
        description="Признак дублирования",
        example=False
    )
    duplicate_for: Optional[uuid.UUID] = Field(
        None,
        description="Идентификатор видео в формате UUID4",
        example="0003d59f-89cb-4c5c-9156-6c5bc07c6fad"
    )
    message: str = Field(
        ...,
        description="Сообщение об успешной загрузке",
        example="Видео успешно загружено"
    )


@app.post(
    "/upload-video",
    response_model=UploadVideoResponse,
    tags=["API для загрузки видео"],
    summary="Загрузка видеофайла",
    responses={
        400: {"description": "Неверный запрос"},
        500: {"description": "Ошибка сервера"}
    }
)
async def upload_video(videoFile: UploadFile = File(...)):
    # Проверяем, что файл имеет формат MP4
    if videoFile.content_type != "video/mp4":
        raise HTTPException(status_code=400, detail="Допускаются только файлы MP4.")

    # Генерируем уникальный идентификатор для видео
    video_id = uuid.uuid4()
    filename = f"{video_id}.mp4"
    file_path = os.path.join(UPLOAD_DIR, filename)
    is_duplicate = len(file_path) % 2 == 0
    print(f'{file_path=}')

    try:
        # Читаем содержимое файла в байты
        video_bytes = await videoFile.read()
        video_size = len(video_bytes)
        print(f'{video_size=}')
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при чтении файла.") from e
    finally:
        videoFile.file.close()

    if is_duplicate:
        return UploadVideoResponse(
            is_duplicate=True,
            duplicate_for=video_id,
            message = "Видео успешно загружено"
        )
    else:
        return UploadVideoResponse(
            is_duplicate=False,
            duplicate_for=None,
            message = "Видео успешно загружено"
        )