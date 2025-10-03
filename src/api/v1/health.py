from typing import AsyncIterator

from starlette.responses import JSONResponse, Response

from api.utils import streamer
from core.api import NBERequest, NDJsonStreamingResponse
from node.api.base import NodeApi
from node.models.health import Health


async def get(request: NBERequest) -> Response:
    response = await request.app.state.node_api.get_health_check()
    return JSONResponse(response)


async def _health_iterator(node_api: NodeApi) -> AsyncIterator[Health]:
    while True:
        yield await node_api.get_health_check()


async def stream(request: NBERequest) -> Response:
    _stream = _health_iterator(request.app.state.node_api)
    health_stream = streamer(stream=_stream, interval=2)
    return NDJsonStreamingResponse(health_stream)
