from http.client import SERVICE_UNAVAILABLE

from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse

from . import STATIC_DIR

INDEX_FILE = STATIC_DIR.joinpath("index.html")


def spa(path: str) -> FileResponse:
    if path.startswith(("api", "static")):
        raise HTTPException(SERVICE_UNAVAILABLE, detail="Routing is incorrectly configured.")
    return FileResponse(INDEX_FILE)


def create_frontend_router() -> APIRouter:
    router = APIRouter()
    router.get("/{path:path}", include_in_schema=False)(spa)
    return router
