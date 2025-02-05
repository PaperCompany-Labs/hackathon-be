import os
from pathlib import Path
from typing import Optional
from uuid import uuid4

from database import get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from novel.novel_query import create_novel, create_novel_shorts
from novel.novel_schema import (
    NovelCreateWithAdmin,
    NovelResponse,
    NovelShortsCreate,
    NovelShortsResponse,
)
from sqlalchemy.orm import Session


# 현재 파일의 디렉토리를 기준으로 .env 파일 경로 설정
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

ADMIN_CODE = os.getenv("ADMIN_CODE", "admin_code")

app = APIRouter(prefix="/admin")

# 음악 파일 저장 경로 설정
UPLOAD_DIR = Path(__file__).parent.parent / "uploads" / "music"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def save_music_file(file: UploadFile) -> str:
    """음악 파일을 저장하고 저장된 경로를 반환"""
    if not file:
        return None

    # 파일 확장자 검증
    allowed_extensions = {".mp3", ".wav", ".ogg"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="지원하지 않는 음악 파일 형식입니다")

    # 고유한 파일명 생성
    unique_filename = f"{uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    # 파일 저장
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        return str(file_path.relative_to(Path(__file__).parent.parent))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 저장 중 오류 발생: {str(e)}")


@app.post("/novel", response_model=NovelResponse, description="[관리자] 소설 생성")
async def create_novel_endpoint(request: NovelCreateWithAdmin, db: Session = Depends(get_db)):
    # 관리자 코드 검증
    if request.admin_code != ADMIN_CODE:
        raise HTTPException(status_code=403, detail="잘못된 관리자 코드입니다")

    result = create_novel(db, request.novel_data)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@app.post("/shorts", response_model=NovelShortsResponse, description="[관리자] 숏츠 생성")
async def create_shorts_endpoint(
    admin_code: str,
    novel_no: int,
    form_type: int,
    content: str,
    image: Optional[str] = None,
    music_file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    # 관리자 코드 검증
    if admin_code != ADMIN_CODE:
        raise HTTPException(status_code=403, detail="잘못된 관리자 코드입니다")

    # 음악 파일 처리
    music_path = None
    if music_file:
        music_path = await save_music_file(music_file)

    # 숏츠 데이터 생성
    shorts_data = NovelShortsCreate(
        novel_no=novel_no, form_type=form_type, content=content, image=image, music=music_path
    )

    result = create_novel_shorts(db, shorts_data)
    if not result.success:
        # 실패 시 업로드된 파일 삭제
        if music_path:
            os.remove(UPLOAD_DIR / Path(music_path).name)
        raise HTTPException(status_code=400, detail=result.message)

    return result
