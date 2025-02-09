from comment.comment_schema import (
    CommentActionResponse,
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    CommentUpdate,
)
from models import Comment, NovelShorts, UserLike
from sqlalchemy import update
from sqlalchemy.orm import Session


def get_comments(db: Session, novel_shorts_no: int) -> CommentListResponse:
    try:
        comments = (
            db.query(Comment)
            .filter(Comment.novel_shorts_no == novel_shorts_no, Comment.is_del.is_(False))
            .order_by(Comment.created_date.asc())
            .all()
        )

        if not comments:
            return CommentListResponse(success=True, message="댓글이 없습니다", comments=[])

        # 댓글 변환
        comment_list = []
        for comment in comments:
            try:
                comment_dict = {
                    "no": comment.no,
                    "novel_shorts_no": comment.novel_shorts_no,
                    "user_no": comment.user_no,
                    "parent_no": comment.parent_no,
                    "content": comment.content,
                    "like": comment.like,
                    "created_date": comment.created_date,
                    "is_del": comment.is_del,
                }
                comment_response = CommentResponse(**comment_dict)
                comment_list.append(comment_response)
            except Exception as e:
                print(f"Error converting comment {comment.no}: {str(e)}")
                continue

        return CommentListResponse(success=True, message="댓글을 성공적으로 조회했습니다", comments=comment_list)
    except Exception as e:
        print(f"Error in get_comments: {str(e)}")
        return CommentListResponse(success=False, message="댓글 조회 중 오류가 발생했습니다", comments=[])


def create_comment(db: Session, comment_data: CommentCreate) -> CommentActionResponse:
    try:
        # 숏츠 존재 여부 확인
        shorts = db.query(NovelShorts).filter(NovelShorts.no == comment_data.novel_shorts_no).first()
        if not shorts:
            return CommentActionResponse(success=False, message="존재하지 않는 숏츠입니다")

        # 부모 댓글 존재 여부 확인 (대댓글인 경우)
        if comment_data.parent_no:
            parent_comment = db.query(Comment).filter(Comment.no == comment_data.parent_no).first()
            if not parent_comment:
                return CommentActionResponse(success=False, message="존재하지 않는 부모 댓글입니다")

        # 새 댓글 생성
        new_comment = Comment(
            novel_shorts_no=comment_data.novel_shorts_no,
            user_no=comment_data.user_no,
            content=comment_data.content,
            parent_no=comment_data.parent_no,
        )

        db.add(new_comment)

        # 숏츠의 댓글 수 증가
        shorts.comments += 1

        db.commit()
        db.refresh(new_comment)

        return CommentActionResponse(success=True, message="댓글이 작성되었습니다", comment_no=new_comment.no)

    except Exception as e:
        print(f"Error in create_comment: {str(e)}")  # 에러 로깅 추가
        db.rollback()
        return CommentActionResponse(success=False, message=f"댓글 작성 중 오류가 발생했습니다: {str(e)}")


def update_comment(db: Session, comment_no: int, user_no: int, update_data: CommentUpdate) -> CommentActionResponse:
    try:
        comment = (
            db.query(Comment)
            .filter(
                Comment.no == comment_no,
                Comment.user_no == user_no,
                Comment.is_del.is_(False),
            )
            .first()
        )

        if not comment:
            return CommentActionResponse(success=False, message="수정할 댓글을 찾을 수 없습니다")

        if not update_data.content.strip():
            return CommentActionResponse(success=False, message="댓글 내용을 입력해주세요")

        comment.content = update_data.content
        db.commit()

        return CommentActionResponse(success=True, message="댓글이 수정되었습니다")
    except Exception as e:
        print(f"Error in update_comment: {str(e)}")
        db.rollback()
        return CommentActionResponse(success=False, message="댓글 수정 중 오류가 발생했습니다")


def delete_comment(db: Session, comment_no: int, user_no: int) -> CommentActionResponse:
    try:
        comment = (
            db.query(Comment)
            .filter(
                Comment.no == comment_no,
                Comment.user_no == user_no,
                Comment.is_del.is_(False),
            )
            .first()
        )

        if not comment:
            return CommentActionResponse(success=False, message="삭제할 댓글을 찾을 수 없습니다")

        comment.is_del = True

        # NovelShorts의 댓글 수 감소
        stmt = (
            update(NovelShorts)
            .where(NovelShorts.no == comment.novel_shorts_no)
            .values(comments=NovelShorts.comments - 1)
        )
        db.execute(stmt)

        db.commit()
        return CommentActionResponse(success=True, message="댓글이 삭제되었습니다")
    except Exception as e:
        print(f"Error in delete_comment: {str(e)}")
        db.rollback()
        return CommentActionResponse(success=False, message="댓글 삭제 중 오류가 발생했습니다")


def like_comment(db: Session, user_no: int, comment_no: int) -> CommentActionResponse:
    try:
        # 댓글 존재 여부 확인
        comment = db.query(Comment).filter(Comment.no == comment_no, Comment.is_del.is_(False)).first()
        if not comment:
            return CommentActionResponse(success=False, message="존재하지 않는 댓글입니다")

        # 이미 좋아요를 눌렀는지 확인
        existing_like = (
            db.query(UserLike)
            .filter(UserLike.user_no == user_no, UserLike.comment_no == comment_no, UserLike.is_del.is_(False))
            .first()
        )

        if existing_like:
            return CommentActionResponse(success=False, message="이미 좋아요를 눌렀습니다")

        # 새로운 좋아요 기록 생성 또는 기존 기록 업데이트
        like_record = db.query(UserLike).filter(UserLike.user_no == user_no, UserLike.comment_no == comment_no).first()

        if like_record:
            like_record.is_del = False
        else:
            like_record = UserLike(user_no=user_no, comment_no=comment_no)
            db.add(like_record)

        # 댓글의 좋아요 수 증가
        comment.like += 1
        db.commit()

        return CommentActionResponse(success=True, message="댓글에 좋아요를 눌렀습니다")

    except Exception as e:
        print(f"Error in like_comment: {str(e)}")
        db.rollback()
        return CommentActionResponse(success=False, message="좋아요 처리 중 오류가 발생했습니다")


def dislike_comment(db: Session, user_no: int, comment_no: int) -> CommentActionResponse:
    try:
        # 댓글 존재 여부 확인
        comment = db.query(Comment).filter(Comment.no == comment_no, Comment.is_del.is_(False)).first()
        if not comment:
            return CommentActionResponse(success=False, message="존재하지 않는 댓글입니다")

        # 좋아요 기록 확인
        like_record = (
            db.query(UserLike)
            .filter(UserLike.user_no == user_no, UserLike.comment_no == comment_no, UserLike.is_del.is_(False))
            .first()
        )

        if not like_record:
            return CommentActionResponse(success=False, message="좋아요 기록이 없습니다")

        # 좋아요 취소 처리
        like_record.is_del = True
        comment.like -= 1
        db.commit()

        return CommentActionResponse(success=True, message="댓글 좋아요를 취소했습니다")

    except Exception as e:
        print(f"Error in dislike_comment: {str(e)}")
        db.rollback()
        return CommentActionResponse(success=False, message="좋아요 취소 처리 중 오류가 발생했습니다")
