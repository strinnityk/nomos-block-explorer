from datetime import datetime
from typing import List

from starlette.responses import Response

from api.streams import into_ndjson_stream
from core.api import NBERequest, NDJsonStreamingResponse
from node.models.transactions import Transaction
from utils.datetime import increment_datetime


async def stream(request: NBERequest) -> Response:
    bootstrap_transactions: List[Transaction] = await request.app.state.transaction_repository.get_latest(
        limit=5, descending=False
    )
    highest_timestamp: datetime = max(
        (transaction.timestamp for transaction in bootstrap_transactions), default=datetime.min
    )
    updates_stream = request.app.state.transaction_repository.updates_stream(
        timestamp_from=increment_datetime(highest_timestamp)
    )
    transaction_stream = into_ndjson_stream(stream=updates_stream, bootstrap_data=bootstrap_transactions)
    return NDJsonStreamingResponse(transaction_stream)
