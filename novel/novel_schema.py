from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PostResponse(BaseModel):
    no: int

    # 소설 정보
    title: str
    author: str
    description: str
    genres: Optional[List[str]] = None
    cover_image: Optional[str] = None
    chapters: int  # 연재수
    views: int  # 조회수
    recommends: int  # 추천수
    created_date: datetime
    last_uploaded_date: Optional[datetime] = None
    source_platform: str
    source_url: str

    # 숏츠 반응
    likes: int
    saves: int
    comments: int

    # 숏츠 컨텐츠
    content: str
    image: str
    music: str


class LikeResponse(BaseModel):
    success: bool
    message: str
    likes: int


class SaveResponse(BaseModel):
    success: bool
    message: str
    saves: int
