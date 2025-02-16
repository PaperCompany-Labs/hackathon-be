from datetime import datetime
from functools import wraps
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import traceback
from typing import Callable


# logs 디렉토리 생성
os.makedirs("logs", exist_ok=True)

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(
            "logs/comment_api.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("comment_api")


def log_api_call(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 함수 이름과 시작 시간 기록
        start_time = datetime.now()
        func_name = func.__name__

        # 요청 파라미터 로깅
        request_params = {"args": str(args), "kwargs": {k: str(v) for k, v in kwargs.items() if k != "db"}}

        logger.info(f"API 호출 시작 - {func_name}")
        logger.info(f"요청 파라미터: {json.dumps(request_params, ensure_ascii=False)}")

        try:
            # 함수 실행
            response = await func(*args, **kwargs)

            # 응답 결과 로깅
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"API 호출 완료 - {func_name}")
            logger.info(f"실행 시간: {execution_time}초")
            logger.info(f"응답 결과: {response}")

            return response

        except Exception as e:
            # 에러 로깅
            logger.error(f"API 호출 실패 - {func_name}")
            logger.error(f"에러 메시지: {str(e)}")
            logger.error(f"스택 트레이스: {traceback.format_exc()}")
            raise

    return wrapper


def log_query(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 함수 이름과 시작 시간 기록
        start_time = datetime.now()
        func_name = func.__name__

        # 쿼리 파라미터 로깅
        query_params = {"args": str(args), "kwargs": {k: str(v) for k, v in kwargs.items() if k != "db"}}

        logger.info(f"쿼리 실행 시작 - {func_name}")
        logger.info(f"쿼리 파라미터: {json.dumps(query_params, ensure_ascii=False)}")

        try:
            # 함수 실행
            result = func(*args, **kwargs)

            # 실행 결과 로깅
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"쿼리 실행 완료 - {func_name}")
            logger.info(f"실행 시간: {execution_time}초")
            logger.info(f"실행 결과: {result}")

            return result

        except Exception as e:
            # 에러 로깅
            logger.error(f"쿼리 실행 실패 - {func_name}")
            logger.error(f"에러 메시지: {str(e)}")
            logger.error(f"스택 트레이스: {traceback.format_exc()}")
            raise

    return wrapper
