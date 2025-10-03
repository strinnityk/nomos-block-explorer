from starlette.requests import Request
from starlette.responses import ContentStream, StreamingResponse

from core.app import NBE


class NBERequest(Request):
    app: NBE


class NDJsonStreamingResponse(StreamingResponse):
    def __init__(self, content: ContentStream):
        super().__init__(
            content,
            media_type="application/x-ndjson",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
