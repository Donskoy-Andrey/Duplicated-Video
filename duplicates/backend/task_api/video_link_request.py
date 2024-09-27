from pydantic import BaseModel


class VideoLinkRequest(BaseModel):
    link: str
