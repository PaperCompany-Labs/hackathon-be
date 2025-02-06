from comment import comment_router
from database import engine
from fastapi import FastAPI
from fastapi.openapi.models import SecuritySchemeIn, SecuritySchemeType
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse
import models
from novel import admin_router, novel_router
from starlette.middleware.cors import CORSMiddleware
from user import user_router
from user.user_router import active_router


models.Base.metadata.create_all(bind=engine)

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Novel Shorts API",
        version="1.0.0",
        description="Novel Shorts API Documentation",
        routes=app.routes,
    )

    # JWT Bearer 토큰 인증 설정
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": SecuritySchemeType.http,
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "in": SecuritySchemeIn.header,
        }
    }

    # 모든 엔드포인트에 보안 요구사항 적용
    openapi_schema["security"] = [{"Bearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
