from comment.comment_query import (
    create_comment,
    delete_comment,
    dislike_comment,
    get_comments,
    like_comment,
)
from comment.comment_schema import CommentActionResponse, CommentCreate, CommentListResponse
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from user.user_router import get_current_user


app = APIRouter(prefix="/shorts")


@app.get("/{shorts_no}/comments", response_model=CommentListResponse)
async def get_shorts_comments(shorts_no: int, db: Session = Depends(get_db)):
    result = get_comments(db, shorts_no)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@app.post("/comment", response_model=CommentActionResponse)
async def create_shorts_comment(
    comment_data: CommentCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다")

    # user_no를 토큰에서 가져온 값으로 설정
    comment_data.user_no = current_user["user_no"]

    result = create_comment(db, comment_data)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


# @app.put("/comment/{comment_no}", response_model=CommentActionResponse)
# async def update_shorts_comment(
#     comment_no: int,
#     update_data: CommentUpdate,
#     current_user: dict = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     if not current_user:
#         raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다")

#     result = update_comment(db, comment_no, current_user["user_no"], update_data)
#     if not result.success:
#         raise HTTPException(status_code=400, detail=result.message)
#     return result


@app.delete("/comment/{comment_no}", response_model=CommentActionResponse)
async def delete_shorts_comment(
    comment_no: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다")

    result = delete_comment(db, comment_no, current_user["user_no"])
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@app.post("/comment/{comment_no}/like", response_model=CommentActionResponse)
async def like_shorts_comment(
    comment_no: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다")

    result = like_comment(db, comment_no)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@app.delete("/comment/{comment_no}/like", response_model=CommentActionResponse)
async def dislike_shorts_comment(
    comment_no: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요한 서비스입니다")

    result = dislike_comment(db, comment_no)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


"""
# 댓글 조회
GET /novel/shorts/123/comments

# 댓글 작성
POST /novel/shorts/comment
{
    "novel_shorts_no": 123,
    "user_no": 456,
    "content": "댓글 내용"
}

# 대댓글 작성
POST /novel/shorts/comment
{
    "novel_shorts_no": 123,
    "user_no": 456,
    "parent_no": 789,
    "content": "대댓글 내용"
}

# 댓글 수정
PUT /novel/shorts/comment/789?user_no=456
{
    "content": "수정된 내용"
}

# 댓글 삭제
DELETE /novel/shorts/comment/789?user_no=456

# 댓글 좋아요
POST /novel/shorts/comment/789/like
"""
