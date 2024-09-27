from pydantic import BaseModel


class VideoLinkRequestBody(BaseModel):
    link: str
