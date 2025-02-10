from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CommentCreate(BaseModel):
    novel_shorts_no: int
    parent_no: Optional[int] = None
    content: str
    user_no: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "novel_shorts_no": 1,
                "content": "댓글 내용",
                "parent_no": None,
            }
        }


class CommentUpdate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    no: int
    novel_shorts_no: int
    user_no: int
    user_name: str
    parent_no: Optional[int]
    content: str
    like: int
    created_date: datetime
    is_del: bool

    class Config:
        json_schema_extra = {
            "example": {
                "no": 1,
                "novel_shorts_no": 1,
                "user_no": 1,
                "user_name": "작성자",
                "parent_no": None,
                "content": "댓글 내용",
                "like": 0,
                "created_date": "2024-02-09T12:00:00",
                "is_del": False,
            }
        }


class CommentListResponse(BaseModel):
    success: bool
    message: str
    comments: List[CommentResponse]


class CommentActionResponse(BaseModel):
    success: bool
    message: str
    comment_no: Optional[int] = None
