import os

from dotenv import load_dotenv
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)

        if not credentials:
            raise HTTPException(status_code=403, detail="인증 토큰이 없습니다.")

        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=403, detail="올바르지 않은 인증 방식입니다.")

        try:
            payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            user_no: int = payload.get("user_no")

            if not user_id or not user_no:
                raise HTTPException(status_code=403, detail="올바르지 않은 토큰입니다.")

            return {"user_id": user_id, "user_no": user_no}

        except JWTError:
            raise HTTPException(status_code=403, detail="토큰이 만료되었거나 올바르지 않습니다.")
