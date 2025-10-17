from typing import List

from fastapi import Query
from starlette.responses import Response

from api.streams import into_ndjson_stream
from core.api import NBERequest, NDJsonStreamingResponse
from node.models.blocks import Block


async def _prefetch_blocks(request: NBERequest, prefetch_limit: int) -> List[Block]:
    return (
        []
        if prefetch_limit == 0 else
        await request.app.state.block_repository.get_latest(limit=prefetch_limit, ascending=True)
    )


async def stream(request: NBERequest, prefetch_limit: int = Query(0, alias="prefetch-limit", ge=0)) -> Response:
    bootstrap_blocks: List[Block] = await _prefetch_blocks(request, prefetch_limit)
    highest_slot: int = max((block.slot for block in bootstrap_blocks), default=0)
    updates_stream = request.app.state.block_repository.updates_stream(slot_from=highest_slot + 1)
    block_stream = into_ndjson_stream(stream=updates_stream, bootstrap_data=bootstrap_blocks)
    return NDJsonStreamingResponse(block_stream)
