import os
from pathlib import Path
from typing import Optional
from uuid import uuid4

from database import get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from models import NovelShorts
from novel.novel_query import (
    create_novel,
    create_novel_shorts,
    get_novel_detail,
    get_novel_shorts_csv,
    update_shorts_media,
)
from novel.novel_schema import (
    NovelCreateWithAdmin,
    NovelDetailResponse,
    NovelResponse,
    NovelShortsCreateWithAdmin,
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


def verify_admin_code(code: str) -> bool:
    return code == ADMIN_CODE


@app.post("/shorts", response_model=NovelShortsResponse, description="[관리자] 숏츠 생성")
async def create_shorts_endpoint(shorts_data: NovelShortsCreateWithAdmin, db: Session = Depends(get_db)):
    # 관리자 코드 검증
    if not verify_admin_code(shorts_data.admin_code):
        raise HTTPException(status_code=403, detail="관리자 권한이 없습니다")

    # 음악 파일 처리 (있는 경우)
    music_path = None
    if shorts_data.music_file:
        try:
            music_path = await save_file(shorts_data.music_file, "music")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"음악 파일 업로드 중 오류 발생: {str(e)}")

    # 숏츠 생성
    result = create_novel_shorts(db, shorts_data.shorts_data, music_path)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)

    return result


async def process_media_files(shorts: NovelShorts, image_file: Optional[UploadFile], music_file: Optional[UploadFile]):
    """미디어 파일 처리 및 저장"""
    music_path = None
    image_path = None
    old_paths = []

    if music_file and music_file.filename:
        music_path = await save_file(music_file, "music")
        if shorts.music:
            old_paths.append(shorts.music)

    if image_file and image_file.filename:
        image_path = await save_file(image_file, "image")
        if shorts.image:
            old_paths.append(shorts.image)

    return music_path, image_path, old_paths


@app.put("/shorts/{shorts_no}/media", response_model=NovelShortsResponse, description="[관리자] 숏츠 미디어 업데이트")
async def update_shorts_media_endpoint(
    shorts_no: int,
    admin_code: str = Form(...),
    image_file: Optional[UploadFile] = None,
    music_file: Optional[UploadFile] = None,
    db: Session = Depends(get_db),
):
    if admin_code != ADMIN_CODE:
        raise HTTPException(status_code=403, detail="잘못된 관리자 코드입니다")

    try:
        shorts = db.query(NovelShorts).filter(NovelShorts.no == shorts_no).first()
        if not shorts:
            raise HTTPException(status_code=404, detail="존재하지 않는 숏츠입니다")

        music_path, image_path, old_paths = await process_media_files(shorts, image_file, music_file)

        result = update_shorts_media(
            db,
            shorts_no,
            image=image_path if image_path is not None else shorts.image,
            music=music_path if music_path is not None else shorts.music,
        )

        if result.success:
            for old_path in old_paths:
                if old_path and os.path.exists(UPLOAD_DIR / old_path):
                    os.remove(UPLOAD_DIR / old_path)
            return result

        raise HTTPException(status_code=400, detail=result.message)

    except Exception as e:
        if music_path and os.path.exists(UPLOAD_DIR / music_path):
            os.remove(UPLOAD_DIR / music_path)
        if image_path and os.path.exists(UPLOAD_DIR / image_path):
            os.remove(UPLOAD_DIR / image_path)
        raise e


@app.get("/novel/{novel_no}", response_model=NovelDetailResponse, description="[관리자] 소설 상세 정보 조회")
async def read_novel_detail(
    novel_no: int,
    admin_code: str = Form(...),
    db: Session = Depends(get_db),
):
    if admin_code != ADMIN_CODE:
        raise HTTPException(status_code=403, detail="잘못된 관리자 코드입니다")

    result = get_novel_detail(db, novel_no)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["msg"])
    return result


@app.get(
    "/novel/export/csv",
    response_class=PlainTextResponse,
    description="[관리자] 소설 및 숏츠 데이터 CSV 추출",
)
async def export_novel_shorts_csv(
    admin_code: str,
    db: Session = Depends(get_db),
):
    if admin_code != ADMIN_CODE:
        raise HTTPException(status_code=403, detail="잘못된 관리자 코드입니다")

    csv_content, data = get_novel_shorts_csv(db)
    if not csv_content:
        raise HTTPException(status_code=404, detail="데이터가 없습니다")

    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment;filename=novel_shorts_data.csv"},
    )
