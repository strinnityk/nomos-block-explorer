from fastapi import APIRouter
from starlette.responses import FileResponse

from . import STATIC_DIR

INDEX_FILE = STATIC_DIR.joinpath("index.html")


def spa() -> FileResponse:
    return FileResponse(INDEX_FILE)


def create_frontend_router() -> APIRouter:
    router = APIRouter()
    router.get("/", include_in_schema=False)(spa)
    return router
