from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class NewUserForm(BaseModel):
    id: str = Field(..., min_length=1, max_length=10)
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=1, max_length=10)
    gender: Literal["M", "F", "X"] = Field(..., description="성별 (M/F/X)")
    age: int = Field(..., ge=0, le=150)

    @field_validator("id", "password", "name", "gender")
    def check_empty(cls, v: str) -> str:
        if not v or v.isspace():
            raise ValueError("필수 항목을 입력해주세요")
        return v

    @field_validator("password")
    def validate_password(cls, v: str) -> str:
        if not any(char.isdigit() for char in v):
            raise ValueError("비밀번호는 숫자를 포함해야 합니다")
        if not any(char.isalpha() for char in v):
            raise ValueError("비밀번호는 영문을 포함해야 합니다")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {"id": "testuser", "password": "Test1234!", "name": "테스트", "gender": "M", "age": 25}
        }
    }


class LoginForm(BaseModel):
    id: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserActiveCreate(BaseModel):
    novel_no: Optional[int] = None
    novel_shorts_no: Optional[int] = None
    comment_no: Optional[int] = None
    active_type: int
    acted_date: datetime = datetime.now()


class UserActiveResponse(BaseModel):
    success: bool
    message: str
