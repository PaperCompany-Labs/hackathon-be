from comment import comment_router
from database import engine
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import RedirectResponse
import models
from novel import admin_router, novel_router
from starlette.middleware.cors import CORSMiddleware
from user import user_router
from user.user_router import active_router


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Novel Shorts API",
    description="Novel Shorts API Documentation",
    version="1.0.0",
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 미들웨어
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# 라우터 등록
app.include_router(user_router.app, tags=["user"])
app.include_router(novel_router.app, tags=["novel"])
app.include_router(comment_router.app, tags=["comment"])
app.include_router(active_router, prefix="/user", tags=["user"])
app.include_router(admin_router.app, tags=["admin"])


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health_check")
async def health_check():
    return {"state": "ok"}
