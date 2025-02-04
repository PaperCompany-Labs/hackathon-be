from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ADMIN_CODE: str = "default_admin_code"  # 기본값 설정

    class Config:
        env_file = ".env"


settings = Settings()
