import torch
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File

from .api.base import videoLinkRequest, videoLinkResponse, videoRequestFront, videoLinkResponseFront
from .api.utils import video_url_to_tensor, send_video_to_triton, search_in_faiss, video_bytes_to_tensor, \
    search_duplicate

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
    await search_duplicate(video.link)

@app.post("/check-video-duplicate",
          response_model=videoLinkResponse,
          responses={
              400: {"description": "Неверный запрос"},
              500: {"description": "Ошибка сервера"}
          },
          tags=["API для проверки дубликатов видео"],
          summary="Проверка видео на дублирование")
async def check_video_duplicate(videoLink: videoLinkRequest):
    await search_duplicate(videoLink.link)

@app.post(
    "/upload-video",
    response_model=videoLinkResponseFront,
    tags=["API для загрузки видео"],
    summary="Загрузка видеофайла",
    responses={
        400: {"description": "Неверный запрос"},
        500: {"description": "Ошибка сервера"}
    }
)
async def upload_video(videoFile: UploadFile = File(...)):
    if videoFile.content_type != "video/mp4":
        raise HTTPException(status_code=400, detail="Допускаются только файлы MP4.")

    video_bytes = await videoFile.read()
    await search_duplicate(video_bytes)



@app.post("/test_request")
async def test_request():
    # Examples
    # url = 'https://s3.ritm.media/yappy-db-duplicates/16a91af7-f3ac-4517-a051-5240b30f3217.mp4'
    # url = 'https://s3.ritm.media/yappy-db-duplicates/000be48d-c88c-4d48-8b7a-28430ac9b57d.mp4'

    # Duplicate
    # url = 'https://s3.ritm.media/yappy-db-duplicates/b5f191e6-42e0-43f5-8773-560643de17fb.mp4'

    # Original
    url = 'https://s3.ritm.media/yappy-db-duplicates/55635719-38d9-4adb-b455-4c852ed869e9.mp4'

    video_tensor_short, video_tensor_long = await asyncio.to_thread(video_url_to_tensor, url)
    query_embeddings = await asyncio.to_thread(send_video_to_triton, video_tensor_short, video_tensor_long)
    query_embeddings = torch.tensor(query_embeddings)
    output = search_in_faiss(query_embeddings=query_embeddings)

    print(output)
    print(query_embeddings.shape)
    return {"result": True}
