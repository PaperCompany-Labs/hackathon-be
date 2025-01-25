from datetime import datetime, timedelta
import os
from typing import Optional

from database import get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from user import user_query, user_schema


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = APIRouter(prefix="/user")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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
    response: Response,
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

        # 쿠키에 토큰 저장
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=int(ACCESS_TOKEN_EXPIRE_MINUTES * 60),
            samesite="lax",
        )

        return user_schema.Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"로그인 처리 중 오류가 발생했습니다: {str(e)}"
        )


@app.post(path="/logout")
async def logout(request: Request, response: Response):
    try:
        # 토큰 존재 여부 확인
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="이미 로그아웃된 상태입니다")

        # 토큰 형식 검증
        if not token.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="잘못된 토큰 형식입니다")

        try:
            # 토큰 유효성 검증
            token = token.split("Bearer ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if not payload:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다")
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="만료되었거나 유효하지 않은 토큰입니다"
            )

        # 쿠키 삭제
        response.delete_cookie(key="access_token", httponly=True, samesite="lax")

        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "로그아웃되었습니다"})

    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="로그아웃 처리 중 오류가 발생했습니다"
        )


# JWT 토큰 검증을 위한 의존성 함수
async def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[dict]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="로그인이 필요합니다",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        raise credentials_exception

    try:
        token = token.split("Bearer ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_no: int = payload.get("user_no")

        if user_id is None:
            raise credentials_exception

        return {"user_id": user_id, "user_no": user_no}
    except JWTError:
        raise credentials_exception
