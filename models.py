from datetime import datetime
import enum

from database import Base
from sqlalchemy import ARRAY, SMALLINT, VARCHAR, Boolean, Column, DateTime, ForeignKey, Integer, Text


"""
no: 내부적으로 사용하는 식별자(인덱스)
id: 외부에서 주입된 식별자
"""


class User(Base):
    __tablename__ = "user"

    no = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(VARCHAR(10), nullable=True)
    password = Column(VARCHAR(100), nullable=True)
    name = Column(VARCHAR(10), nullable=True)
    gender = Column(VARCHAR(1), nullable=False, default="X")
    age = Column(SMALLINT, nullable=False, default=0)
    created_date = Column(DateTime, nullable=False, default=datetime.now)


# class UserPreference(Base):
#     __tablename__ = "user_preference"

#     no = Column(Integer, primary_key=True, autoincrement=True)
#     user_no = Column(Integer, ForeignKey("user.no"))
#     novel_no = Column(Integer, ForeignKey("novel.no"))
#     genre_type = Column(ARRAY(SMALLINT))
#     degree = Column(Integer)
#     created_date = Column(DateTime, nullable=False, default=datetime.now)


class UserSave(Base):
    __tablename__ = "user_save"

    no = Column(Integer, primary_key=True, autoincrement=True)
    user_no = Column(Integer, ForeignKey("user.no"))
    novel_no = Column(Integer, ForeignKey("novel.no"))
    novel_shorts_no = Column(Integer, ForeignKey("novel_shorts.no"))


class UserActiveLog(Base):
    __tablename__ = "user_active_log"

    no = Column(Integer, primary_key=True, autoincrement=True)
    user_no = Column(Integer, ForeignKey("user.no"))
    novel_no = Column(Integer, ForeignKey("novel.no"), nullable=True)
    comment_no = Column(Integer, ForeignKey("comment.no"), nullable=True)
    active_type = Column(Integer)
    acted_date = Column(DateTime, nullable=True)
    created_date = Column(DateTime, nullable=False, default=datetime.now)


class GenreType(enum.Enum):
    OTHER = 0


class SourceType(enum.Enum):
    OTHER = 0


class SourcePlatformType(enum.Enum):
    OTHER = 0
    MUNPIA = 1
    RIDI = 2


class Novel(Base):
    __tablename__ = "novel"

    no = Column(Integer, primary_key=True, autoincrement=True)
    source_platform_type = Column(SMALLINT)
    source_id = Column(Integer)
    source_type = Column(SMALLINT)
    source_url = Column(Text)
    title = Column(VARCHAR(50))
    author = Column(VARCHAR(50))
    description = Column(Text)
    genres = Column(ARRAY(SMALLINT))
    cover_image = Column(Text)
    chapters = Column(Integer)  # 연재수
    views = Column(Integer)  # 조회수
    recommends = Column(Integer)  # 추천수
    created_date = Column(DateTime, nullable=True)
    last_uploaded_date = Column(DateTime, nullable=True)


# class NovelChapter(Base):
#     __tablename__ = "novel_chapter"

#     no = Column(Integer, primary_key=True, autoincrement=True)
#     novel_no = Column(Integer, ForeignKey("novel.no"))
#     source_id = Column(Integer)  # 주입
#     subtitle = Column(VARCHAR(50))
#     content = Column(Text)


class FormType(enum.Enum):
    OTHER = 0
    TEXT = 1


class NovelShorts(Base):
    __tablename__ = "novel_shorts"

    no = Column(Integer, primary_key=True, autoincrement=True)
    novel_no = Column(Integer, ForeignKey("novel.no"))
    form_type = Column(SMALLINT)
    content = Column(Text)
    image = Column(Text)
    music = Column(Text)
    likes = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    comments = Column(Integer, default=0)


class Comment(Base):
    __tablename__ = "comment"

    no = Column(Integer, primary_key=True, autoincrement=True)
    novel_shorts_no = Column(Integer, ForeignKey("novel_shorts.no"))
    user_no = Column(Integer, ForeignKey("user.no"))
    parent_no = Column(Integer, ForeignKey("comment.no"))
    created_date = Column(DateTime, nullable=False, default=datetime.now)
    is_del = Column(Boolean, nullable=False, default=False)
    content = Column(Text)
    like = Column(Integer, default=0)


class ActiveType(enum.Enum):
    VIEW_START = 1  # 시청 시작
    VIEW_END = 2  # 시청 종료
    LIKE = 3  # 좋아요
    UNLIKE = 4  # 좋아요 취소
    COMMENT = 5  # 덧글
    COMMENT_DELETE = 6  # 덧글 삭제
    COMMENT_UPDATE = 7  # 덧글 수정
    SAVE = 8  # 저장
    UNSAVE = 9  # 저장 취소
    URL_CLICK = 10  # URL 클릭
