from datetime import datetime
from typing import List, Optional

from fastapi import UploadFile
from pydantic import BaseModel


class PostResponse(BaseModel):
    no: int
    form_type: int
    content: str
    music: Optional[str] = None
    views: int
    likes: int
    saves: int
    comments: int
    title: str  # 소설 제목
    author: str  # 작가
    source_url: str  # 원작 URL

    class Config:
        json_schema_extra = {
            "example": {
                "no": 1,
                "form_type": 1,
                "content": "숏츠 내용...",
                "music": "uploads/music/example.mp3",
                "views": 100,
                "likes": 50,
                "saves": 30,
                "comments": 20,
                "title": "소설 제목",
                "author": "작가명",
                "source_url": "https://example.com/novel/123",
            }
        }


class LikeResponse(BaseModel):
    success: bool
    message: str
    likes: int


class SaveResponse(BaseModel):
    success: bool
    message: str
    saves: int


class NovelCreate(BaseModel):
    source_platform_type: int
    source_id: Optional[int] = None
    source_type: int
    source_url: str
    title: str
    author: str
    description: str
    genres: List[int]
    cover_image: Optional[str] = None
    chapters: int = 0
    views: int = 0
    recommends: int = 0
    created_date: Optional[datetime] = None
    last_uploaded_date: Optional[datetime] = None


class NovelShortsCreate(BaseModel):
    novel_id: int  # source_id로 사용될 필드
    content: str

    class Config:
        json_schema_extra = {
            "example": {
                "novel_id": 123,  # 원작 소설의 source_id
                "content": "숏츠 내용...",
            }
        }


class NovelResponse(BaseModel):
    success: bool
    message: str
    novel_no: Optional[int] = None


class NovelShortsResponse(BaseModel):
    success: bool
    message: str
    shorts_no: Optional[int] = None


class AdminRequest(BaseModel):
    admin_code: str


class NovelCreateWithAdmin(AdminRequest):
    novel_data: NovelCreate


class NovelShortsCreateWithAdmin(AdminRequest):
    shorts_data: NovelShortsCreate
    music_file: Optional[UploadFile] = None  # 음악 파일은 선택사항

    class Config:
        json_schema_extra = {
            "example": {
                "admin_code": "your-admin-code",
                "shorts_data": {"novel_id": 123, "content": "숏츠 내용..."},
                "music_file": None,
            }
        }


class CommentResponse(BaseModel):
    no: int
    user_no: int
    content: str
    created_date: datetime
    like: int
    is_del: bool
    parent_no: Optional[int] = None


class NovelShortsWithComments(BaseModel):
    no: int
    form_type: int
    content: str
    image: str
    music: str
    views: int
    likes: int
    saves: int
    comments: List[CommentResponse]


class NovelDetailResponse(BaseModel):
    # 소설 정보
    no: int
    title: str
    author: str
    description: str
    genres: List[int]
    cover_image: str
    chapters: int
    views: int
    recommends: int
    created_date: datetime
    last_uploaded_date: Optional[datetime]
    source_platform_type: int
    source_url: str

    # 숏츠 목록
    shorts_list: List[NovelShortsWithComments]


class NovelShortsMediaUpdate(BaseModel):
    novel_id: int  # source_id로 사용될 필드
    form_type: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "novel_id": 123,  # 원작 소설의 source_id
                "form_type": 1,  # 선택사항
            }
        }


class NovelShortsMediaUpdateWithAdmin(AdminRequest):
    shorts_data: NovelShortsMediaUpdate
    image_file: Optional[UploadFile] = None
    music_file: Optional[UploadFile] = None
