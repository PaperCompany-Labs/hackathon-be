from typing import List

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from novel.novel_query import (
    get_post,
    get_posts,
    like_novel_shorts,
    save_novel_shorts,
    unlike_novel_shorts,
    unsave_novel_shorts,
)
from novel.novel_schema import (
    LikeResponse,
    PostResponse,
    SaveResponse,
)
from sqlalchemy.orm import Session
from user.user_router import get_current_user


app = APIRouter(prefix="/shorts")


@app.get(path="", response_model=List[PostResponse], description="숏츠 - 목록 조회")
async def read_posts(
    limit: int = Query(default=10, ge=1, le=100), offset: int = Query(default=0, ge=0), db: Session = Depends(get_db)
):
    result = get_posts(db, limit, offset)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["msg"])
    return result


@app.get(path="/{post_no}", response_model=PostResponse, description="숏츠 - 상세 조회")
async def read_post(post_no: int, db: Session = Depends(get_db)):
    result = get_post(post_no, db)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["msg"])
    return result


@app.post("/{shorts_no}/like", response_model=LikeResponse, description="숏츠 - 좋아요")
async def like_shorts(shorts_no: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다")

    result = like_novel_shorts(db, shorts_no)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@app.delete("/{shorts_no}/like", response_model=LikeResponse, description="숏츠 - 좋아요 취소")
async def unlike_shorts(shorts_no: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다")

    result = unlike_novel_shorts(db, shorts_no)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@app.post("/{shorts_no}/save", response_model=SaveResponse, description="숏츠 - 저장")
async def save_shorts(shorts_no: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다")

    result = save_novel_shorts(db, current_user["user_no"], shorts_no)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@app.delete("/{shorts_no}/save", response_model=SaveResponse, description="숏츠 - 저장 취소")
async def unsave_shorts(shorts_no: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다")

    result = unsave_novel_shorts(db, current_user["user_no"], shorts_no)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


# @app.post("/novel", response_model=NovelResponse, description="소설 생성")
# async def create_novel_endpoint(
#     novel_data: NovelCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
# ):
#     if not current_user:
#         raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다")

#     result = create_novel(db, novel_data)
#     if not result.success:
#         raise HTTPException(status_code=400, detail=result.message)
#     return result


# @app.post("/shorts", response_model=NovelShortsResponse, description="숏츠 생성")
# async def create_shorts_endpoint(
#     shorts_data: NovelShortsCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
# ):
#     if not current_user:
#         raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다")

#     result = create_novel_shorts(db, shorts_data)
#     if not result.success:
#         raise HTTPException(status_code=400, detail=result.message)
#     return result
