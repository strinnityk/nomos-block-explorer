from asyncio import sleep
from typing import AsyncIterable, AsyncIterator, List, Union

from core.models import IdNbeModel

Data = Union[IdNbeModel, List[IdNbeModel]]
Stream = AsyncIterator[Data]


def _parse_stream_data(data: Data) -> bytes:
    if isinstance(data, list):
        return b"".join(item.model_dump_ndjson() for item in data)
    else:
        return data.model_dump_ndjson()


async def streamer(
    stream: Stream,
    bootstrap_data: Data = None,
    interval: int = 5,
) -> AsyncIterable[bytes]:
    if bootstrap_data is not None:
        yield _parse_stream_data(bootstrap_data)

    async for data in stream:
        yield _parse_stream_data(data)
        await sleep(interval)
