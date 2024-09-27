from fastapi import FastAPI

from .task_api import check_video_duplicate, VideoLinkRequestBody, VideoLinkResponse

app = FastAPI()


@app.post("/check-video-duplicate",
          response_model=VideoLinkResponse,
          responses={
              400: {"description": "Неверный запрос"},
              500: {"description": "Ошибка сервера"}
          },
          tags=["API для проверки дубликатов видео"],
          summary="Проверка видео на дублирование")
async def task_api(body: VideoLinkRequestBody):
    return check_video_duplicate(body)
