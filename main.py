from database import engine
from fastapi import FastAPI
import models
from starlette.middleware.cors import CORSMiddleware
from user import user_router


models.Base.metadata.create_all(bind=engine)

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

# app.include_router(user_router.app, tags=["comment"])
# app.include_router(user_router.app, tags=["novel"])
app.include_router(user_router.app, tags=["user"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}
