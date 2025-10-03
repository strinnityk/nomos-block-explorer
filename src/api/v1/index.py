from starlette.responses import JSONResponse, Response

from core.api import NBERequest


async def index(_request: NBERequest) -> Response:
    content = {"version": "1"}
    return JSONResponse(content)
