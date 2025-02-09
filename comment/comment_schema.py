from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CommentCreate(BaseModel):
    novel_shorts_no: int
    parent_no: Optional[int] = None
    content: str


class CommentUpdate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    no: int
    novel_shorts_no: int
    user_no: int
    parent_no: Optional[int]
    content: str
    like: int
    created_date: datetime
    is_del: bool


class CommentListResponse(BaseModel):
    success: bool
    message: str
    comments: List[CommentResponse]


class CommentActionResponse(BaseModel):
    success: bool
    message: str
    comment_no: Optional[int] = None
