from fastapi import HTTPException
from pydantic import BaseModel, field_validator


class NewUserForm(BaseModel):
    id: str
    password: str
    name: str
    gender: str
    age: int

    @field_validator(
        "id",
        "password",
        "name",
        "gender",
        "age",
    )
    def check_empty(cls, v):
        if not v or v.isspace():
            raise HTTPException(status_code=422, detail="필수 항목을 입력해주세요.")
        return v

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise HTTPException(status_code=422, detail="비밀번호는 8자리 이상 영문과 숫자를 포함하여 작성해 주세요.")

        if not any(char.isdigit() for char in v):
            raise HTTPException(status_code=422, detail="비밀번호는 8자리 이상 영문과 숫자를 포함하여 작성해 주세요.")

        if not any(char.isalpha() for char in v):
            raise HTTPException(status_code=422, detail="비밀번호는 8자리 이상 영문과 숫자를 포함하여 작성해 주세요.")

        return v


class Token(BaseModel):
    access_token: str
    token_type: str
