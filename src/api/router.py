from fastapi import APIRouter

from .v1.router import router as v1_router


def create_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(v1_router, prefix="/v1")
    return router
