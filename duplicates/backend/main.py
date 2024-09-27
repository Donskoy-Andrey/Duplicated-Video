from fastapi import FastAPI

from .task_api import check_video_duplicate, VideoLinkRequest

app = FastAPI()


@app.post("/check-video-duplicate")
async def task_api(request: VideoLinkRequest):
    return check_video_duplicate(request)

