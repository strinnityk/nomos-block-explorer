from http.client import NOT_FOUND
from typing import TYPE_CHECKING, AsyncIterator, List, Optional

from fastapi import Path, Query
from starlette.responses import JSONResponse, Response

from api.streams import into_ndjson_stream
from api.v1.serializers.transactions import TransactionRead
from core.api import NBERequest, NDJsonStreamingResponse
from node.models.transactions import Transaction

if TYPE_CHECKING:
    from core.app import NBE


async def _updates_stream(
    app: "NBE", latest_transaction: Optional[Transaction]
) -> AsyncIterator[List[TransactionRead]]:
    _stream = app.state.transaction_repository.updates_stream(transaction_from=latest_transaction)
    async for transactions in _stream:
        yield [TransactionRead.from_transaction(transaction) for transaction in transactions]


async def stream(request: NBERequest, prefetch_limit: int = Query(0, alias="prefetch-limit", ge=0)) -> Response:
    latest_transactions: List[Transaction] = await request.app.state.transaction_repository.get_latest(
        limit=prefetch_limit, ascending=True, preload_relationships=True
    )
    latest_transaction = latest_transactions[-1] if latest_transactions else None
    latest_transaction_read = [TransactionRead.from_transaction(transaction) for transaction in latest_transactions]

    updates_stream: AsyncIterator[List[TransactionRead]] = _updates_stream(request.app, latest_transaction)
    ndjson_transactions_stream = into_ndjson_stream(stream=updates_stream, bootstrap_data=latest_transaction_read)
    return NDJsonStreamingResponse(ndjson_transactions_stream)


async def get(request: NBERequest, transaction_id: int = Path(ge=1)) -> Response:
    transaction = await request.app.state.transaction_repository.get_by_id(transaction_id)
    return transaction.map(
        lambda _transaction: JSONResponse(TransactionRead.from_transaction(_transaction).model_dump(mode="json"))
    ).unwrap_or_else(lambda: Response(status_code=NOT_FOUND))
