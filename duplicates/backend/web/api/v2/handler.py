from fastapi import Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from fastapi.responses import ORJSONResponse
from web.api.v2.router import router
from web.api.v2.base import videoLinkRequest, videoLinkResponse, videoRequestFront, videoLinkResponseFront
from web.api.v2.utils import video_url_to_tensor, send_video_to_triton, search_in_faiss, video_bytes_to_tensor, \
    search_duplicate


@router.post("/check-video-duplicate",
          response_model=videoLinkResponse,
          responses={
              400: {"description": "Неверный запрос"},
              500: {"description": "Ошибка сервера"}
          },
          tags=["API для проверки дубликатов видео"],
          summary="Проверка видео на дублирование")
async def check_video_duplicate(videoLink: videoLinkRequest):
    try:
        # print("1","*"*100)
        has_duplicate,potential_duplicate_uuid = await search_duplicate(videoLink.link)
        # print("2","*"*100)
        # print(has_duplicate,potential_duplicate_uuid)
        # print("3","*"*100)
        if has_duplicate:
            return videoLinkResponse(
                is_duplicate=True, duplicate_for=potential_duplicate_uuid,
            )

        return videoLinkResponse(
            is_duplicate=False, duplicate_for="",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail="Неверный запрос")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера {e}")
