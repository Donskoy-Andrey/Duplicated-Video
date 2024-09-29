from fastapi import UploadFile, File
from pydantic import BaseModel, Field


class videoLinkRequest(BaseModel):
    link: str = Field(
        ...,
        description="ссылка на видео",
        examples=["https://example.com/video.mp4"]
    )


class videoRequestFront(BaseModel):
    link: str = Field(
        ...,
        description="ссылка на видео",
        examples=["https://example.com/video.mp4"]
    )
    confidence_level: float = Field(
        ...,
        description="Уровень уверенности предсказания",
    )


class ResultRequest(BaseModel):
    uid: str