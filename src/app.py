from fastapi import FastAPI

from core.app import NBE
from frontend.statics import mount_statics
from lifespan import lifespan
from router import create_router


def create_app() -> FastAPI:
    app = NBE(lifespan=lifespan)
    app = mount_statics(app)
    app.include_router(create_router())
    return app
