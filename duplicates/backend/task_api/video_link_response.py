from pydantic import BaseModel


class VideoLinkResponse(BaseModel):
    is_duplicate: bool
    duplicate_for: list[str] = []
