import logging
from typing import AsyncIterable, AsyncIterator, List, Union

from core.models import NbeModel, NbeSchema

T = Union[NbeModel, NbeSchema]
Data = Union[T, List[T]]
Stream = AsyncIterator[Data]


logger = logging.getLogger(__name__)


def _into_ndjson_data(data: Data) -> bytes:
    if isinstance(data, list):
        return b"".join(item.model_dump_ndjson() for item in data)
    else:
        return data.model_dump_ndjson()


async def into_ndjson_stream(stream: Stream, *, bootstrap_data: Data = None) -> AsyncIterable[bytes]:
    if bootstrap_data is not None:
        ndjson_data = _into_ndjson_data(bootstrap_data)
        if ndjson_data:
            yield ndjson_data
        else:
            logger.debug("Ignoring streaming bootstrap data because it is empty.")

    async for data in stream:
        ndjson_data = _into_ndjson_data(data)
        if ndjson_data:
            yield ndjson_data
        else:
            logger.debug("Ignoring streaming data because it is empty.")
