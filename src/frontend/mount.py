from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, Response

from src import DIR_REPO

STATIC_DIR = DIR_REPO.joinpath("static")
INDEX_FILE = STATIC_DIR.joinpath("index.html")


def index() -> Response:
    return FileResponse(INDEX_FILE)


def create_frontend_router() -> APIRouter:
    router = APIRouter()

    router.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    router.get("/", include_in_schema=False)(index)

    return router
