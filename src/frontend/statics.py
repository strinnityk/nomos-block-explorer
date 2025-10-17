from starlette.staticfiles import StaticFiles

from core.app import NBE
from frontend import STATIC_DIR


def mount_statics(app: NBE) -> NBE:
    """
    This needs to be mounted onto an app.
    If mounted directly onto a nested router (`include_router`), it will be ignored.
    """
    app.router.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app
