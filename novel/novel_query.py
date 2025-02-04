from models import Novel, NovelShorts, UserSave
from novel.novel_schema import LikeResponse, PostResponse, SaveResponse
from sqlalchemy import delete, update
from sqlalchemy.orm import Session


def get_post(post_no: int, db: Session):
    if not isinstance(post_no, int) or post_no <= 0:
        return {"error": "Invalid post_no", "msg": "올바르지 않은 게시글 번호입니다."}

    if not db or not db.is_active:
        return {"error": "Invalid database session", "msg": "데이터베이스 연결이 유효하지 않습니다."}

    try:
        # 조회수 증가
        view_stmt = update(NovelShorts).where(NovelShorts.no == post_no).values(views=NovelShorts.views + 1)
        db.execute(view_stmt)
        db.commit()

        # 게시글 조회
        post = (
            db.query(
                NovelShorts.no,
                Novel.title,
                Novel.author,
                Novel.description,
                Novel.genres,
                Novel.cover_image,
                Novel.chapters,
                Novel.views,
                Novel.recommends,
                Novel.created_date,
                Novel.last_uploaded_date,
                Novel.source_type,
                Novel.source_url,
                NovelShorts.likes,
                NovelShorts.saves,
                NovelShorts.comments,
                NovelShorts.content,
                NovelShorts.image,
                NovelShorts.music,
                NovelShorts.views.label("shorts_views"),
            )
            .join(Novel, Novel.no == NovelShorts.novel_no)
            .filter(NovelShorts.no == post_no)
            .first()
        )

        if not post:
            return {"error": "Post not found", "msg": "존재하지 않는 번호입니다."}

        return PostResponse(
            no=post.no,
            title=post.title,
            author=post.author,
            description=post.description,
            genres=post.genres,
            cover_image=post.cover_image,
            chapters=post.chapters,
            views=post.shorts_views,
            recommends=post.recommends,
            created_date=post.created_date,
            last_uploaded_date=post.last_uploaded_date,
            source_platform=str(post.source_type),
            source_url=post.source_url,
            likes=post.likes,
            saves=post.saves,
            comments=post.comments,
            content=post.content,
            image=post.image,
            music=post.music,
        )
    except Exception as e:
        db.rollback()  # 에러 발생 시 롤백
        return {"error": str(e), "msg": "게시글을 가져오는 중 오류가 발생했습니다."}


def get_posts(db: Session, limit: int = 10, offset: int = 0):
    try:
        posts = (
            db.query(
                NovelShorts.no,
                Novel.title,
                Novel.author,
                Novel.description,
                Novel.genres,
                Novel.cover_image,
                Novel.chapters,
                Novel.views,
                Novel.recommends,
                Novel.created_date,
                Novel.last_uploaded_date,
                Novel.source_type,
                Novel.source_url,
                NovelShorts.likes,
                NovelShorts.saves,
                NovelShorts.comments,
                NovelShorts.content,
                NovelShorts.image,
                NovelShorts.music,
            )
            .join(Novel, Novel.no == NovelShorts.novel_no)
            .order_by(NovelShorts.no.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        if not posts:
            return []

        result_list = []
        for post in posts:
            try:
                post_dict = {
                    "no": post.no,
                    "title": post.title,
                    "author": post.author,
                    "description": post.description,
                    "genres": post.genres,
                    "cover_image": post.cover_image,
                    "chapters": post.chapters,
                    "views": post.views,
                    "recommends": post.recommends,
                    "created_date": post.created_date,
                    "last_uploaded_date": post.last_uploaded_date,
                    "source_platform": str(post.source_type),
                    "source_url": post.source_url,
                    "likes": post.likes,
                    "saves": post.saves,
                    "comments": post.comments,
                    "content": post.content,
                    "image": post.image,
                    "music": post.music,
                }
                result_list.append(post_dict)
            except Exception as e:
                print(f"Error converting post {post.no}: {str(e)}")
                continue

        return result_list

    except Exception as e:
        print(f"Error in get_posts: {str(e)}")
        return {"error": str(e), "msg": "게시글 목록을 가져오는 중 오류가 발생했습니다."}


def like_novel_shorts(db: Session, novel_shorts_no: int) -> LikeResponse:
    try:
        # 좋아요 수 증가
        stmt = (
            update(NovelShorts)
            .where(NovelShorts.no == novel_shorts_no)
            .values(likes=NovelShorts.likes + 1)
            .returning(NovelShorts.likes)
        )
        result = db.execute(stmt)
        db.commit()

        updated_likes = result.scalar()
        return LikeResponse(success=True, message="좋아요를 눌렀습니다", likes=updated_likes)
    except Exception:
        db.rollback()
        return LikeResponse(success=False, message="좋아요 처리 중 오류가 발생했습니다", likes=-1)


def unlike_novel_shorts(db: Session, novel_shorts_no: int) -> LikeResponse:
    try:
        # 좋아요 수 감소
        stmt = (
            update(NovelShorts)
            .where(NovelShorts.no == novel_shorts_no, NovelShorts.likes > 0)
            .values(likes=NovelShorts.likes - 1)
            .returning(NovelShorts.likes)
        )
        result = db.execute(stmt)
        db.commit()

        updated_likes = result.scalar()
        return LikeResponse(success=True, message="좋아요를 취소했습니다", likes=updated_likes)
    except Exception:
        db.rollback()
        return LikeResponse(success=False, message="좋아요 취소 처리 중 오류가 발생했습니다", likes=-1)


def save_novel_shorts(db: Session, user_no: int, novel_shorts_no: int) -> SaveResponse:
    try:
        # 이미 저장했는지 확인
        existing = (
            db.query(UserSave).filter(UserSave.user_no == user_no, UserSave.novel_shorts_no == novel_shorts_no).first()
        )

        if existing:
            return SaveResponse(success=False, message="이미 저장된 게시물입니다", saves=-1)

        # 저장 처리
        new_save = UserSave(user_no=user_no, novel_shorts_no=novel_shorts_no)
        db.add(new_save)

        # 저장 수 증가
        stmt = (
            update(NovelShorts)
            .where(NovelShorts.no == novel_shorts_no)
            .values(saves=NovelShorts.saves + 1)
            .returning(NovelShorts.saves)
        )
        result = db.execute(stmt)
        db.commit()

        updated_saves = result.scalar()
        return SaveResponse(success=True, message="저장되었습니다", saves=updated_saves)
    except Exception:
        db.rollback()
        return SaveResponse(success=False, message="저장 처리 중 오류가 발생했습니다", saves=-1)


def unsave_novel_shorts(db: Session, user_no: int, novel_shorts_no: int) -> SaveResponse:
    try:
        # 저장 기록 삭제
        delete_stmt = delete(UserSave).where(UserSave.user_no == user_no, UserSave.novel_shorts_no == novel_shorts_no)
        result = db.execute(delete_stmt)

        if result.rowcount == 0:
            return SaveResponse(success=False, message="저장되지 않은 게시물입니다", saves=-1)

        # 저장 수 감소
        update_stmt = (
            update(NovelShorts)
            .where(NovelShorts.no == novel_shorts_no, NovelShorts.saves > 0)
            .values(saves=NovelShorts.saves - 1)
            .returning(NovelShorts.saves)
        )
        result = db.execute(update_stmt)
        db.commit()

        updated_saves = result.scalar()
        return SaveResponse(success=True, message="저장이 취소되었습니다", saves=updated_saves)
    except Exception:
        db.rollback()
        return SaveResponse(success=False, message="저장 취소 처리 중 오류가 발생했습니다", saves=-1)
