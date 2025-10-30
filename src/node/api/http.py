import logging
from typing import AsyncIterator, List
from urllib.parse import urljoin

import httpx
import requests

from node.api.base import NodeApi
from node.api.serializers.block import BlockSerializer
from node.api.serializers.health import HealthSerializer

logger = logging.getLogger(__name__)


class HttpNodeApi(NodeApi):
    ENDPOINT_INFO = "/cryptarchia/info"
    ENDPOINT_TRANSACTIONS = "/cryptarchia/transactions"
    ENDPOINT_BLOCKS = "/cryptarchia/blocks"
    ENDPOINT_BLOCKS_STREAM = "/cryptarchia/blocks/stream"

    def __init__(self, host: str, port: int, protocol: str = "http", timeout: int = 60):
        self.host: str = host
        self.port: int = port
        self.protocol: str = protocol
        self.timeout: int = timeout

    @property
    def base_url(self):
        return f"{self.protocol}://{self.host}:{self.port}"

    async def get_health(self) -> HealthSerializer:
        url = urljoin(self.base_url, self.ENDPOINT_INFO)
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            return HealthSerializer.from_healthy()
        else:
            return HealthSerializer.from_unhealthy()

    async def get_blocks(self, slot_from: int, slot_to: int) -> List[BlockSerializer]:
        query_string = f"slot_from={slot_from}&slot_to={slot_to}"
        endpoint = urljoin(self.base_url, self.ENDPOINT_BLOCKS)
        url = f"{endpoint}?{query_string}"
        response = requests.get(url, timeout=60)
        python_json = response.json()
        blocks = [BlockSerializer.model_validate(item) for item in python_json]
        return blocks

    async def get_blocks_stream(self) -> AsyncIterator[BlockSerializer]:
        url = urljoin(self.base_url, self.ENDPOINT_BLOCKS_STREAM)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()  # TODO: Result

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        block = BlockSerializer.model_validate_json(line)
                    except Exception as e:
                        import traceback

                        traceback.print_exc()
                        raise e
                    logger.debug(f"Received new block from Node: {block}")
                    yield block
