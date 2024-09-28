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
        description="Уровень уверенности предсказания",
    )
    confidence_level: float


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

class videoLinkResponseFront(BaseModel):
    is_duplicate: bool = Field(
        ...,
        description="признак дублирования",
        examples=[False]
    )
    link_duplicate: str = Field(
        ...,
        description="ссылки на видео",
        examples=[
            "https://s3.ritm.media/yappy-db-duplicates/0003d59f-89cb-4c5c-9156-6c5bc07c6fad.mp4",
            "https://s3.ritm.media/yappy-db-duplicates/000ab50a-e0bd-4577-9d21-f1f426144321.mp4",
        ]
    )
