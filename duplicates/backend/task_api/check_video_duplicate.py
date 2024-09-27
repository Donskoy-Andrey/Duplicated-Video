from pathlib import Path
import requests

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .video_link_response import VideoLinkResponse
from .video_link_request import VideoLinkRequestBody


def check_video_duplicate(body: VideoLinkRequestBody):
    download_video_response = requests.get(body.link)
    if not download_video_response.ok or download_video_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Unable to download file by link")

    try:
        with open(Path("/app/data/test.mp4"), "wb") as file:
            file.write(download_video_response.content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unable to save file, traceback: {e}")

    # Даем файл ml, получаем на выходе тензор?
    # ---------------------------

    # ---------------------------
    # Шаблон ответа

    api_response: VideoLinkResponse = VideoLinkResponse(is_duplicate=False)
    return JSONResponse(content=api_response.model_dump(), status_code=200)