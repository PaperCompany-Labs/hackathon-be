from auth.jwt_bearer import JWTBearer
from comment.comment_query import (
    create_comment,
    delete_comment,
    dislike_comment,
    get_comments,
    like_comment,
    update_comment,
)
from comment.comment_schema import CommentActionResponse, CommentCreate, CommentListResponse, CommentUpdate
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils.logger import log_api_call


app = APIRouter(prefix="/shorts")
jwt_bearer = JWTBearer()


@app.get("/{shorts_no}/comments", response_model=CommentListResponse)
@log_api_call
async def get_shorts_comments(shorts_no: int, db: Session = Depends(get_db)):
    result = get_comments(db, shorts_no)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@app.post("/comment", response_model=CommentActionResponse)
@log_api_call
async def create_shorts_comment(
    comment_data: CommentCreate, current_user: dict = Depends(jwt_bearer), db: Session = Depends(get_db)
):
    comment_data.user_no = current_user["user_no"]
    result = create_comment(db, comment_data)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@app.put("/comment/{comment_no}", response_model=CommentActionResponse)
@log_api_call
async def update_shorts_comment(
    comment_no: int,
    update_data: CommentUpdate,
    current_user: dict = Depends(jwt_bearer),
    db: Session = Depends(get_db),
):
    result = update_comment(db, comment_no, current_user["user_no"], update_data)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@app.delete("/comment/{comment_no}", response_model=CommentActionResponse)
@log_api_call
async def delete_shorts_comment(
    comment_no: int, current_user: dict = Depends(jwt_bearer), db: Session = Depends(get_db)
):
    result = delete_comment(db, comment_no, current_user["user_no"])
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@app.post("/comment/{comment_no}/like", response_model=CommentActionResponse)
@log_api_call
async def like_shorts_comment(comment_no: int, current_user: dict = Depends(jwt_bearer), db: Session = Depends(get_db)):
    result = like_comment(db, current_user["user_no"], comment_no)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@app.delete("/comment/{comment_no}/like", response_model=CommentActionResponse)
@log_api_call
async def dislike_shorts_comment(
    comment_no: int, current_user: dict = Depends(jwt_bearer), db: Session = Depends(get_db)
):
    result = dislike_comment(db, current_user["user_no"], comment_no)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result
