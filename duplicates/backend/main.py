import torch
import asyncio
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File, Form

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
    try:
        has_duplicate,potential_duplicate_uuid = await search_duplicate(video.link)
        print(has_duplicate,potential_duplicate_uuid)
        if has_duplicate:
            print('2*'*100)
            return videoLinkResponseFront(
                is_duplicate=True, link_duplicate=f"https://s3.ritm.media/yappy-db-duplicates/{potential_duplicate_uuid}.mp4",
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
        has_duplicate,potential_duplicate_uuid = await search_duplicate(videoLink.link)
        print(has_duplicate,potential_duplicate_uuid)
        if has_duplicate:
            print('2*'*100)
            return videoLinkResponse(
                is_duplicate=True, duplicate_for=potential_duplicate_uuid,
            )

        return videoLinkResponse(
            is_duplicate=False, duplicate_for="",
        )
        print('3*'*100)

    except ValueError as e:
        raise HTTPException(status_code=400, detail="Неверный запрос")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@app.post(
    "/check-video-file-duplicate-front",
    response_model=videoLinkResponseFront,
    tags=["API для загрузки видео"],
    summary="Загрузка видеофайла",
    responses={
        400: {"description": "Неверный запрос"},
        500: {"description": "Ошибка сервера"}
    }
)
async def upload_video(file: UploadFile = File(...), confidenceLevel: float=Form(...)):
    print(file.content_type)  # Отладочное сообщение
    if file.content_type != "video/mp4":
        raise HTTPException(status_code=400, detail="Допускаются только файлы MP4.")


    try:
        video_bytes = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            print('ssssssssssss')
            temp_video.write(video_bytes)
            print('aaaaaa')
            temp_video.flush()
            temp_video.close()
            print(temp_video)
        print("2", "*"*100)

        has_duplicate,potential_duplicate_uuid = await search_duplicate(temp_video.name)
        print("3", "*"*100)
        print(has_duplicate,potential_duplicate_uuid)
        if has_duplicate:
            print('4', '*'*100)
            return videoLinkResponseFront(
                is_duplicate=True, link_duplicate=f"https://s3.ritm.media/yappy-db-duplicates/{potential_duplicate_uuid}.mp4",
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
