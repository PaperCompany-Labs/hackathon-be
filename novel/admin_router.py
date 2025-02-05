import os
from pathlib import Path
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

# 파일 저장 경로 설정
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
MUSIC_DIR = UPLOAD_DIR / "music"
IMAGE_DIR = UPLOAD_DIR / "images"
MUSIC_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


async def save_file(file: UploadFile, file_type: str) -> str:
    """파일을 저장하고 저장된 경로를 반환"""
    if not file:
        return ""  # 파일이 없으면 빈 문자열 반환

    # 파일 확장자 검증
    allowed_extensions = {"music": {".mp3", ".wav", ".ogg"}, "image": {".jpg", ".jpeg", ".png", ".gif"}}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions[file_type]:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 {file_type} 파일 형식입니다")

    # 저장 디렉토리 선택
    save_dir = MUSIC_DIR if file_type == "music" else IMAGE_DIR

    # 고유한 파일명 생성
    unique_filename = f"{uuid4()}{file_ext}"
    file_path = save_dir / unique_filename

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
    image_file: UploadFile = File(None),
    music_file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    # 관리자 코드 검증
    if admin_code != ADMIN_CODE:
        raise HTTPException(status_code=403, detail="잘못된 관리자 코드입니다")

    # 파일 처리
    music_path = ""
    image_path = ""
    try:
        if music_file:
            music_path = await save_file(music_file, "music")
        if image_file:
            image_path = await save_file(image_file, "image")

        # 숏츠 데이터 생성
        shorts_data = NovelShortsCreate(
            novel_no=novel_no, form_type=form_type, content=content, image=image_path, music=music_path
        )

        result = create_novel_shorts(db, shorts_data)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)

        return result

    except Exception as e:
        # 실패 시 업로드된 파일들 삭제
        if music_path and os.path.exists(UPLOAD_DIR / music_path):
            os.remove(UPLOAD_DIR / music_path)
        if image_path and os.path.exists(UPLOAD_DIR / image_path):
            os.remove(UPLOAD_DIR / image_path)
        raise e
