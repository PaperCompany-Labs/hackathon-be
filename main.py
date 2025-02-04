from comment import comment_router
from database import engine
from fastapi import FastAPI
import models
from novel import novel_router
from novel.admin_router import admin_router
from starlette.middleware.cors import CORSMiddleware
from user import user_router
from user.user_router import active_router


models.Base.metadata.create_all(bind=engine)

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

app.include_router(user_router.app, tags=["user"])
app.include_router(novel_router.app, tags=["novel"])
app.include_router(comment_router.app, tags=["comment"])
app.include_router(active_router, prefix="/user", tags=["user"])
app.include_router(admin_router, prefix="/api", tags=["admin"])


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"version": "1.0.0"}
