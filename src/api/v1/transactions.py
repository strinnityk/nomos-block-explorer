from datetime import datetime
from typing import List

from fastapi import Query
from starlette.responses import Response

from api.streams import into_ndjson_stream
from core.api import NBERequest, NDJsonStreamingResponse
from node.models.transactions import Transaction
from utils.datetime import increment_datetime


async def _prefetch_transactions(request: NBERequest, prefetch_limit: int) -> List[Transaction]:
    return (
        []
        if prefetch_limit == 0 else
        await request.app.state.transaction_repository.get_latest(limit=prefetch_limit, descending=False)
    )


async def stream(request: NBERequest, prefetch_limit: int = Query(0, alias="prefetch-limit", ge=0)) -> Response:
    bootstrap_transactions: List[Transaction] = await _prefetch_transactions(request, prefetch_limit)
    highest_timestamp: datetime = max(
        (transaction.timestamp for transaction in bootstrap_transactions), default=datetime.min
    )
    updates_stream = request.app.state.transaction_repository.updates_stream(
        timestamp_from=increment_datetime(highest_timestamp)
    )
    transaction_stream = into_ndjson_stream(stream=updates_stream, bootstrap_data=bootstrap_transactions)
    return NDJsonStreamingResponse(transaction_stream)
