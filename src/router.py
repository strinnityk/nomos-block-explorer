from functools import partial, update_wrapper
from os import environ
from urllib.request import Request

from fastapi import APIRouter
from starlette.responses import JSONResponse, Response

from api.router import create_api_router
from frontend import create_frontend_router


async def _debug_router(_request: Request, *_, router: APIRouter) -> Response:
    content = [
        {
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods),
        }
        for route in router.routes
    ]
    return JSONResponse(content)


def create_router() -> APIRouter:
    router = APIRouter()

    debug_router = partial(_debug_router, router=router)
    update_wrapper(debug_router, _debug_router)

    router.include_router(create_api_router(), prefix="/api")
    if bool(environ.get("DEBUG")):
        router.add_route("/debug", debug_router)
    router.include_router(create_frontend_router())

    return router
