from datetime import datetime

from database import Base
from sqlalchemy import VARCHAR, Boolean, Column, DateTime, ForeignKey, Integer, Text


class User(Base):
    __tablename__ = "user"

    no = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(VARCHAR(10), nullable=True)
    password = Column(VARCHAR(100), nullable=True)
    name = Column(VARCHAR(10), nullable=True)
    gender = Column(VARCHAR(1), nullable=False, default="0")
    age = Column(Integer, nullable=False, default=0)
    created_date = Column(DateTime, nullable=False, default=datetime.now)


# class UserPreference(Base):
#     __tablename__ = "user_preference"

#     no = Column(Integer, primary_key=True, autoincrement=True)
#     user_no = Column(Integer, ForeignKey("user.no"))
#     novel_no = Column(Integer, ForeignKey("novel.no"))
#     genre_no = Column(Integer, ForeignKey("genre.no"))
#     degree = Column(Integer)
#     created_date = Column(DateTime, nullable=False, default=datetime.now)

# class Genre(Base):
#     __tablename__ = "genre"
#     no = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(VARCHAR(50))


class UserActiveLog(Base):
    __tablename__ = "user_active_log"

    no = Column(Integer, primary_key=True, autoincrement=True)
    user_no = Column(Integer, ForeignKey("user.no"))
    novel_no = Column(Integer, ForeignKey("novel.no"), nullable=True)
    comment_no = Column(Integer, ForeignKey("comment.no"), nullable=True)
    active_no = Column(Integer, ForeignKey("active.no"))
    acted_date = Column(DateTime, nullable=True)
    created_date = Column(DateTime, nullable=False, default=datetime.now)


class Active(Base):
    __tablename__ = "active"

    no = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(50))


class Novel(Base):
    __tablename__ = "novel"

    no = Column(Integer, primary_key=True)  # 주입
    title = Column(VARCHAR(50))
    description = Column(Text)
    author = Column(VARCHAR(50))
    cover_image = Column(Text)


class NovelChapter(Base):
    __tablename__ = "novel_chapter"

    no = Column(Integer, primary_key=True, autoincrement=True)
    novel_no = Column(Integer, ForeignKey("novel.no"))
    subtitle = Column(VARCHAR(50))
    content = Column(Text)


class NovelShorts(Base):
    __tablename__ = "novel_shorts"

    no = Column(Integer, primary_key=True, autoincrement=True)
    novel_no = Column(Integer, ForeignKey("novel.no"))
    chapter_no = Column(Integer, ForeignKey("novel_chapter.no"))
    content = Column(Text)
    music = Column(VARCHAR(100))
    like = Column(Integer, default=0)
    save = Column(Integer, default=0)


class Comment(Base):
    __tablename__ = "comment"

    no = Column(Integer, primary_key=True, autoincrement=True)
    novel_no = Column(Integer, ForeignKey("novel.no"))
    user_no = Column(Integer, ForeignKey("user.no"))
    parent_no = Column(Integer, ForeignKey("comment.no"))
    created_date = Column(DateTime, nullable=False, default=datetime.now)
    is_del = Column(Boolean, nullable=False, default=False)
    content = Column(Text)
    like = Column(Integer, default=0)
