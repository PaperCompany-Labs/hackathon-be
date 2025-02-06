from datetime import datetime, timedelta
import os
from typing import Optional

from database import get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from user import user_query, user_schema
from user.user_query import create_active_log
from user.user_schema import UserActiveCreate, UserActiveResponse


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = APIRouter(prefix="/user")
active_router = APIRouter(prefix="/active")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[dict]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="로그인이 필요합니다",
        headers={"WWW-Authenticate": "Bearer"},
    )

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise credentials_exception

    try:
        token = auth_header.split("Bearer ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_no: int = payload.get("user_no")

        if user_id is None:
            raise credentials_exception

        return {"user_id": user_id, "user_no": user_no}
    except JWTError:
        raise credentials_exception


@app.post(path="/signup")
async def signup(new_user: user_schema.NewUserForm, db: Session = Depends(get_db)):
    try:
        # 회원 존재 여부 확인
        user = user_query.get_user(db, new_user.id)
        if user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 아이디입니다")

        # 회원 가입
        user_query.create_user(new_user, db)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "회원가입이 완료되었습니다"})
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        print(f"Signup error: {str(e)}")  # 에러 로깅
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="회원가입 처리 중 오류가 발생했습니다"
        )


@app.post(path="/login", response_model=user_schema.Token)
async def login(
    login_form: user_schema.LoginForm,
    db: Session = Depends(get_db),
):
    # 회원 존재 여부 확인
    user = user_query.get_user(db, login_form.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="아이디 또는 비밀번호가 일치하지 않습니다")

    # 비밀번호 검증
    if not user_query.verify_password(login_form.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="아이디 또는 비밀번호가 일치하지 않습니다")

    try:
        # 액세스 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id, "user_no": user.no}, expires_delta=access_token_expires
        )

        return user_schema.Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"로그인 처리 중 오류가 발생했습니다: {str(e)}"
        )


@app.post(path="/logout", security=[{"Bearer": []}])
async def logout(request: Request, current_user: dict = Depends(get_current_user)):
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "로그아웃되었습니다"})

    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="로그아웃 처리 중 오류가 발생했습니다"
        )


@active_router.post("/log", response_model=UserActiveResponse, security=[{"Bearer": []}])
async def log_user_activity(
    active_data: UserActiveCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다")

    result = create_active_log(db, current_user["user_no"], active_data)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)

    return result
