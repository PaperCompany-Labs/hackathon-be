import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# 현재 파일의 디렉토리를 기준으로 .env 파일 경로 설정
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)  # override=True로 설정하여 기존 환경변수 덮어쓰기

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# PostgreSQL connection URL
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DB_URL,
    pool_size=50,
    max_overflow=0,
)  # DB 커넥션 풀 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # DB접속을 위한 클래스

Base = declarative_base()  # Base 클래스는 DB 모델 구성할 때 사용


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# META = Base.metadata
# get_db = AsyncDB(DB_URL, meta=META, autocommit=False, autoflush=False, expire_on_commit=False)
# DB = Annotated[AsyncSession, Depends(get_db)]
