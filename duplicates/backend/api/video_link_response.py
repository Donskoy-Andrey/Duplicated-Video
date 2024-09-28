import uuid
from typing import Optional

from pydantic import BaseModel, Field


class videoLinkResponse(BaseModel):
    is_duplicate: bool = Field(
        ...,
        description="Признак дублирования",
        example=False
    )
    duplicate_for: str = Field(
        ...,
        description="Идентификатор видео в формате UUID4",
        example="0003d59f-89cb-4c5c-9156-6c5bc07c6fad"
    )


class videoLinkResponseFront(videoLinkResponse):
    link_duplicate: Optional[str] = Field(
        '',
        description="Ссылка на дубликат",
        example="https://s3.ritm.media/yappy-db-duplicates/23fac2f2-7f00-48cb-b3ac-aac8caa3b6b4.mp4"
    )
