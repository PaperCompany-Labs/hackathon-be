import os
from pathlib import Path

from database import get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from novel.novel_query import create_novel, create_novel_shorts
from novel.novel_schema import (
    NovelCreateWithAdmin,
    NovelResponse,
    NovelShortsCreateWithAdmin,
    NovelShortsResponse,
)
from sqlalchemy.orm import Session


# 현재 파일의 디렉토리를 기준으로 .env 파일 경로 설정
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

ADMIN_CODE = os.getenv("ADMIN_CODE", "admin_code")

admin_router = APIRouter()


@admin_router.post("/admin/novel", response_model=NovelResponse, description="[관리자] 소설 생성")
async def create_novel_endpoint(request: NovelCreateWithAdmin, db: Session = Depends(get_db)):
    # 관리자 코드 검증
    if request.admin_code != ADMIN_CODE:
        raise HTTPException(status_code=403, detail="잘못된 관리자 코드입니다")

    result = create_novel(db, request.novel_data)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@admin_router.post("/admin/shorts", response_model=NovelShortsResponse, description="[관리자] 숏츠 생성")
async def create_shorts_endpoint(request: NovelShortsCreateWithAdmin, db: Session = Depends(get_db)):
    # 관리자 코드 검증
    if request.admin_code != ADMIN_CODE:
        raise HTTPException(status_code=403, detail="잘못된 관리자 코드입니다")

    result = create_novel_shorts(db, request.shorts_data)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result
