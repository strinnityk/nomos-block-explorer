from typing import List

from starlette.responses import Response

from api.streams import into_ndjson_stream
from core.api import NBERequest, NDJsonStreamingResponse
from node.models.blocks import Block


async def stream(request: NBERequest) -> Response:
    bootstrap_blocks: List[Block] = await request.app.state.block_repository.get_latest(limit=5, ascending=True)
    highest_slot: int = max((block.slot for block in bootstrap_blocks), default=0)
    updates_stream = request.app.state.block_repository.updates_stream(slot_from=highest_slot + 1)
    block_stream = into_ndjson_stream(stream=updates_stream, bootstrap_data=bootstrap_blocks)
    return NDJsonStreamingResponse(block_stream)
