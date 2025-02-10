import csv
from io import StringIO
from typing import List, Optional, Tuple

from models import Comment, Novel, NovelShorts, UserLike, UserSave
from novel.novel_schema import (
    CommentResponse,
    LikeResponse,
    NovelCreate,
    NovelDetailResponse,
    NovelResponse,
    NovelShortsCreate,
    NovelShortsResponse,
    NovelShortsWithComments,
    PostResponse,
    SaveResponse,
)
from sqlalchemy.orm import Session


def get_post(post_no: int, user_no: Optional[int], db: Session) -> PostResponse:
    try:
        # 게시글 조회
        post = (
            db.query(NovelShorts, Novel)
            .join(Novel, Novel.no == NovelShorts.novel_no)
            .filter(NovelShorts.no == post_no)
            .first()
        )

        if not post:
            return {"error": "Post not found", "msg": "존재하지 않는 숏츠입니다"}

        # 사용자가 좋아요를 눌렀는지 확인
        is_like = False
        if user_no:
            like_exists = (
                db.query(UserLike)
                .filter(
                    UserLike.user_no == user_no,
                    UserLike.novel_shorts_no == post_no,
                    UserLike.is_del.is_(False),
                )
                .first()
            )
            is_like = bool(like_exists)

        return PostResponse(
            no=post.NovelShorts.no,
            form_type=post.NovelShorts.form_type,
            content=post.NovelShorts.content,
            music=post.NovelShorts.music,
            views=post.NovelShorts.views,
            likes=post.NovelShorts.likes,
            saves=post.NovelShorts.saves,
            comments=post.NovelShorts.comments,
            title=post.Novel.title,
            author=post.Novel.author,
            source_url=post.Novel.source_url,
            is_like=is_like,
        )
    except Exception as e:
        print(f"Error in get_post: {str(e)}")
        return {"error": str(e), "msg": "게시글을 가져오는 중 오류가 발생했습니다."}


def get_posts(db: Session, limit: int, offset: int, user_no: Optional[int] = None) -> List[PostResponse]:
    try:
        # 게시글 목록 조회
        posts = (
            db.query(NovelShorts, Novel)
            .join(Novel, Novel.no == NovelShorts.novel_no)
            .order_by(NovelShorts.no.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        # 사용자가 좋아요를 누른 게시글 목록 조회
        user_likes = set()
        if user_no:
            likes = (
                db.query(UserLike.novel_shorts_no)
                .filter(
                    UserLike.user_no == user_no,
                    UserLike.is_del.is_(False),
                )
                .all()
            )
            user_likes = {like[0] for like in likes}

        return [
            PostResponse(
                no=post.NovelShorts.no,
                form_type=post.NovelShorts.form_type,
                content=post.NovelShorts.content,
                music=post.NovelShorts.music,
                views=post.NovelShorts.views,
                likes=post.NovelShorts.likes,
                saves=post.NovelShorts.saves,
                comments=post.NovelShorts.comments,
                title=post.Novel.title,
                author=post.Novel.author,
                source_url=post.Novel.source_url,
                is_like=post.NovelShorts.no in user_likes,
            )
            for post in posts
        ]
    except Exception as e:
        print(f"Error in get_posts: {str(e)}")
        return {"error": str(e), "msg": "숏츠 목록을 가져오는 중 오류가 발생했습니다"}


def like_novel_shorts(db: Session, user_no: int, shorts_no: int) -> LikeResponse:
    try:
        # 숏츠 존재 여부 확인
        shorts = db.query(NovelShorts).filter(NovelShorts.no == shorts_no).first()
        if not shorts:
            return LikeResponse(success=False, message="존재하지 않는 숏츠입니다", likes=0)

        # 이미 좋아요를 눌렀는지 확인
        existing_like = (
            db.query(UserLike)
            .filter(UserLike.user_no == user_no, UserLike.novel_shorts_no == shorts_no, UserLike.is_del.is_(False))
            .first()
        )

        if existing_like:
            return LikeResponse(success=False, message="이미 좋아요를 눌렀습니다", likes=shorts.likes)

        # 새로운 좋아요 기록 생성 또는 기존 기록 업데이트
        like_record = (
            db.query(UserLike).filter(UserLike.user_no == user_no, UserLike.novel_shorts_no == shorts_no).first()
        )

        if like_record:
            like_record.is_del = False
        else:
            like_record = UserLike(user_no=user_no, novel_no=shorts.novel_no, novel_shorts_no=shorts_no)
            db.add(like_record)

        # 숏츠의 좋아요 수 증가
        shorts.likes += 1
        db.commit()

        return LikeResponse(success=True, message="좋아요를 눌렀습니다", likes=shorts.likes)

    except Exception as e:
        print(f"Error in like_novel_shorts: {str(e)}")
        db.rollback()
        return LikeResponse(success=False, message="좋아요 처리 중 오류가 발생했습니다", likes=0)


def unlike_novel_shorts(db: Session, user_no: int, shorts_no: int) -> LikeResponse:
    try:
        # 숏츠 존재 여부 확인
        shorts = db.query(NovelShorts).filter(NovelShorts.no == shorts_no).first()
        if not shorts:
            return LikeResponse(success=False, message="존재하지 않는 숏츠입니다", likes=0)

        # 좋아요 기록 확인
        like_record = (
            db.query(UserLike)
            .filter(UserLike.user_no == user_no, UserLike.novel_shorts_no == shorts_no, UserLike.is_del.is_(False))
            .first()
        )

        if not like_record:
            return LikeResponse(success=False, message="좋아요 기록이 없습니다", likes=shorts.likes)

        # 좋아요 취소 처리
        like_record.is_del = True
        shorts.likes -= 1
        db.commit()

        return LikeResponse(success=True, message="좋아요를 취소했습니다", likes=shorts.likes)

    except Exception as e:
        print(f"Error in unlike_novel_shorts: {str(e)}")
        db.rollback()
        return LikeResponse(success=False, message="좋아요 취소 중 오류가 발생했습니다", likes=0)


def save_novel_shorts(db: Session, user_no: int, shorts_no: int) -> SaveResponse:
    try:
        # 숏츠 존재 여부 확인
        shorts = db.query(NovelShorts).filter(NovelShorts.no == shorts_no).first()
        if not shorts:
            return SaveResponse(success=False, message="존재하지 않는 숏츠입니다", saves=0)

        # 이미 저장했는지 확인
        existing_save = (
            db.query(UserSave)
            .filter(UserSave.user_no == user_no, UserSave.novel_shorts_no == shorts_no, UserSave.is_del.is_(False))
            .first()
        )

        if existing_save:
            return SaveResponse(success=False, message="이미 저장된 숏츠입니다", saves=shorts.saves)

        # 새로운 저장 기록 생성 또는 기존 기록 업데이트
        save_record = (
            db.query(UserSave).filter(UserSave.user_no == user_no, UserSave.novel_shorts_no == shorts_no).first()
        )

        if save_record:
            save_record.is_del = False
        else:
            save_record = UserSave(user_no=user_no, novel_no=shorts.novel_no, novel_shorts_no=shorts_no)
            db.add(save_record)

        # 숏츠의 저장 수 증가
        shorts.saves += 1
        db.commit()

        return SaveResponse(success=True, message="숏츠를 저장했습니다", saves=shorts.saves)

    except Exception as e:
        print(f"Error in save_novel_shorts: {str(e)}")
        db.rollback()
        return SaveResponse(success=False, message="저장 처리 중 오류가 발생했습니다", saves=0)


def unsave_novel_shorts(db: Session, user_no: int, shorts_no: int) -> SaveResponse:
    try:
        # 숏츠 존재 여부 확인
        shorts = db.query(NovelShorts).filter(NovelShorts.no == shorts_no).first()
        if not shorts:
            return SaveResponse(success=False, message="존재하지 않는 숏츠입니다", saves=0)

        # 저장 기록 확인
        save_record = (
            db.query(UserSave)
            .filter(UserSave.user_no == user_no, UserSave.novel_shorts_no == shorts_no, UserSave.is_del.is_(False))
            .first()
        )

        if not save_record:
            return SaveResponse(success=False, message="저장 기록이 없습니다", saves=shorts.saves)

        # 저장 취소 처리
        save_record.is_del = True
        shorts.saves -= 1
        db.commit()

        return SaveResponse(success=True, message="저장을 취소했습니다", saves=shorts.saves)

    except Exception as e:
        print(f"Error in unsave_novel_shorts: {str(e)}")
        db.rollback()
        return SaveResponse(success=False, message="저장 취소 중 오류가 발생했습니다", saves=0)


def create_novel(db: Session, novel_data: NovelCreate) -> NovelResponse:
    try:
        # 이미 존재하는 소설인지 확인
        existing_novel = (
            db.query(Novel)
            .filter(
                Novel.source_platform_type == novel_data.source_platform_type, Novel.source_id == novel_data.source_id
            )
            .first()
        )

        if existing_novel:
            return NovelResponse(success=False, message="이미 존재하는 소설입니다", novel_no=existing_novel.no)

        # 새 소설 생성
        new_novel = Novel(**novel_data.model_dump())
        db.add(new_novel)
        db.commit()
        db.refresh(new_novel)

        return NovelResponse(success=True, message="소설이 생성되었습니다", novel_no=new_novel.no)
    except Exception as e:
        print(f"Error in create_novel: {str(e)}")
        db.rollback()
        return NovelResponse(success=False, message="소설 생성 중 오류가 발생했습니다")


def get_novel_no_by_source_id(db: Session, source_id: int) -> Optional[int]:
    """소설의 source_id로 novel_no를 찾아오는 함수"""
    novel = db.query(Novel.no).filter(Novel.source_id == source_id).first()
    return novel.no if novel else None


def create_novel_shorts(
    db: Session, shorts_data: NovelShortsCreate, music_path: Optional[str] = None
) -> NovelShortsResponse:
    try:
        novel_no = get_novel_no_by_source_id(db, shorts_data.novel_id)
        if not novel_no:
            return NovelShortsResponse(success=False, message="해당하는 소설을 찾을 수 없습니다")

        new_shorts = NovelShorts(
            novel_no=novel_no,
            content=shorts_data.content,
            form_type=1,
            music=music_path,
        )

        db.add(new_shorts)
        db.commit()
        db.refresh(new_shorts)

        return NovelShortsResponse(success=True, message="숏츠가 생성되었습니다", shorts_no=new_shorts.no)
    except Exception as e:
        db.rollback()
        print(f"Error creating shorts: {str(e)}")
        return NovelShortsResponse(success=False, message="숏츠 생성 중 오류가 발생했습니다")


def get_novel_detail(db: Session, novel_no: int):
    try:
        # 소설 정보 조회
        novel = db.query(Novel).filter(Novel.no == novel_no).first()
        if not novel:
            return {"error": "Novel not found", "msg": "존재하지 않는 소설입니다"}

        # 숏츠 및 댓글 정보 조회
        shorts_list = (
            db.query(NovelShorts).filter(NovelShorts.novel_no == novel_no).order_by(NovelShorts.no.desc()).all()
        )

        # 각 숏츠의 댓글 조회
        result_shorts = []
        for shorts in shorts_list:
            comments = (
                db.query(Comment)
                .filter(Comment.novel_shorts_no == shorts.no, Comment.is_del.is_(False))
                .order_by(Comment.created_date.asc())
                .all()
            )

            comments_response = [
                CommentResponse(
                    no=comment.no,
                    user_no=comment.user_no,
                    content=comment.content,
                    created_date=comment.created_date,
                    like=comment.like,
                    is_del=comment.is_del,
                    parent_no=comment.parent_no,
                )
                for comment in comments
            ]

            shorts_with_comments = NovelShortsWithComments(
                no=shorts.no,
                form_type=shorts.form_type,
                content=shorts.content,
                image=shorts.image,
                music=shorts.music,
                views=shorts.views,
                likes=shorts.likes,
                saves=shorts.saves,
                comments=comments_response,
            )
            result_shorts.append(shorts_with_comments)

        return NovelDetailResponse(
            no=novel.no,
            title=novel.title,
            author=novel.author,
            description=novel.description,
            genres=novel.genres,
            cover_image=novel.cover_image,
            chapters=novel.chapters,
            views=novel.views,
            recommends=novel.recommends,
            created_date=novel.created_date,
            last_uploaded_date=novel.last_uploaded_date,
            source_platform_type=novel.source_platform_type,
            source_url=novel.source_url,
            shorts_list=result_shorts,
        )

    except Exception as e:
        print(f"Error in get_novel_detail: {str(e)}")
        return {"error": str(e), "msg": "소설 정보를 가져오는 중 오류가 발생했습니다"}


def update_shorts_media(
    db: Session, shorts_no: int, image: Optional[str] = None, music: Optional[str] = None
) -> NovelShortsResponse:
    try:
        shorts = db.query(NovelShorts).filter(NovelShorts.no == shorts_no).first()
        if not shorts:
            return NovelShortsResponse(success=False, message="존재하지 않는 숏츠입니다")

        update_data = {}
        if image is not None:
            update_data["image"] = image
        if music is not None:
            update_data["music"] = music

        if update_data:
            db.query(NovelShorts).filter(NovelShorts.no == shorts_no).update(update_data)
            db.commit()

        return NovelShortsResponse(success=True, message="미디어가 업데이트되었습니다", shorts_no=shorts_no)
    except Exception as e:
        print(f"Error in update_shorts_media: {str(e)}")
        db.rollback()
        return NovelShortsResponse(success=False, message="미디어 업데이트 중 오류가 발생했습니다")


def get_novel_shorts_csv(db: Session) -> Tuple[str, List[dict]]:
    try:
        # 소설과 숏츠 조인하여 데이터 조회
        results = (
            db.query(
                Novel.no.label("novel_no"),
                NovelShorts.no.label("novel_short_no"),
                NovelShorts.content,
                NovelShorts.views,
                NovelShorts.likes,
                NovelShorts.saves,
            )
            .join(NovelShorts, Novel.no == NovelShorts.novel_no)
            .order_by(Novel.no, NovelShorts.no)
            .all()
        )

        if not results:
            return "", []

        # CSV 파일 생성
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["novel_no", "novel_short_no", "content", "views", "likes", "saves"])

        data = []
        for row in results:
            data_row = {
                "novel_no": row.novel_no,
                "novel_short_no": row.novel_short_no,
                "content": row.content,
                "views": row.views,
                "likes": row.likes,
                "saves": row.saves,
            }
            data.append(data_row)
            writer.writerow(data_row.values())

        return output.getvalue(), data

    except Exception as e:
        print(f"Error in get_novel_shorts_csv: {str(e)}")
        return "", []


def update_shorts_media_by_novel_id(
    db: Session,
    novel_id: int,
    form_type: Optional[int] = None,
    image_path: Optional[str] = None,
    music_path: Optional[str] = None,
) -> NovelShortsResponse:
    try:
        # source_id로 novel_no 찾기
        novel_no = get_novel_no_by_source_id(db, novel_id)
        if not novel_no:
            return NovelShortsResponse(success=False, message="해당하는 소설을 찾을 수 없습니다")

        # novel_no로 모든 shorts 찾기
        shorts_list = db.query(NovelShorts).filter(NovelShorts.novel_no == novel_no).all()
        if not shorts_list:
            return NovelShortsResponse(success=False, message="해당하는 숏츠가 없습니다")

        # 모든 shorts 업데이트
        for shorts in shorts_list:
            if form_type is not None:
                shorts.form_type = form_type
            if image_path:
                shorts.image = image_path
            if music_path:
                shorts.music = music_path

        db.commit()
        return NovelShortsResponse(success=True, message="숏츠가 업데이트되었습니다")

    except Exception as e:
        db.rollback()
        print(f"Error updating shorts media: {str(e)}")
        return NovelShortsResponse(success=False, message="숏츠 업데이트 중 오류가 발생했습니다")
