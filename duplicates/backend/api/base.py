from pydantic import BaseModel, Field


class videoLinkRequest(BaseModel):
    link: str = Field(
        ...,
        description="ссылка на видео",
        examples=["https://example.com/video.mp4"]
    )


class videoLinkResponse(BaseModel):
    is_duplicate: bool = Field(
        ...,
        description="признак дублирования",
        examples=[False]
    )
    duplicate_for: str = Field(
        ...,
        description="идентификтаор видео в формате uuid4",
        examples=["0003d59f-89cb-4c5c-9156-6c5bc07c6fad", "000ab50a-e0bd-4577-9d21-f1f426144321"]
    )
