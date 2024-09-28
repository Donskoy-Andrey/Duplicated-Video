from pydantic import BaseModel, Field, HttpUrl


class videoLinkRequest(BaseModel):
    link: HttpUrl = Field(
        ...,
        description="Ссылка на видео",
        example="https://example.com/video.mp4"
    )
