from http.client import NOT_FOUND
from typing import TYPE_CHECKING, AsyncIterator, List, Optional

from fastapi import Path, Query
from starlette.responses import JSONResponse, Response

from api.streams import into_ndjson_stream
from api.v1.serializers.blocks import BlockRead
from core.api import NBERequest, NDJsonStreamingResponse
from node.models.blocks import Block

if TYPE_CHECKING:
    from core.app import NBE


async def _get_latest(request: NBERequest, limit: int) -> List[BlockRead]:
    blocks = await request.app.state.block_repository.get_latest(limit=limit, ascending=True)
    return [BlockRead.from_block(block) for block in blocks]


async def _prefetch_blocks(request: NBERequest, prefetch_limit: int) -> List[BlockRead]:
    return [] if prefetch_limit == 0 else await _get_latest(request, prefetch_limit)


async def _updates_stream(app: "NBE", latest_block: Optional[Block]) -> AsyncIterator[List[BlockRead]]:
    _stream = app.state.block_repository.updates_stream(block_from=latest_block)
    async for blocks in _stream:
        yield [BlockRead.from_block(block) for block in blocks]


async def stream(request: NBERequest, prefetch_limit: int = Query(0, alias="prefetch-limit", ge=0)) -> Response:
    bootstrap_blocks: List[BlockRead] = await _prefetch_blocks(request, prefetch_limit)
    latest_block = bootstrap_blocks[-1] if bootstrap_blocks else None
    updates_stream: AsyncIterator[List[BlockRead]] = _updates_stream(request.app, latest_block)
    ndjson_blocks_stream = into_ndjson_stream(stream=updates_stream, bootstrap_data=bootstrap_blocks)
    return NDJsonStreamingResponse(ndjson_blocks_stream)


async def get(request: NBERequest, block_id: int = Path(ge=1)) -> Response:
    block = await request.app.state.block_repository.get_by_id(block_id)
    return block.map(lambda _block: JSONResponse(BlockRead.from_block(_block).model_dump(mode="json"))).unwrap_or_else(
        lambda: Response(status_code=NOT_FOUND)
    )
