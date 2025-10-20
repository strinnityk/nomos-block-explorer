from fastapi import APIRouter

from .v1.router import create_v1_router


def create_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(create_v1_router(), prefix="/v1")
    return router
