from urllib.parse import urljoin

import requests

from node.api.base import NodeApi


class HttpNodeApi(NodeApi):
    ENDPOINT_MANTLE_STATUS = "/mantle/status"
    ENDPOINT_MANTLE_TRANSACTIONS = "/mantle/transactions"
    ENDPOINT_MANTLE_BLOCKS = "/mantle/blocks"

    def __init__(self, host: str, port: int, protocol: str = "http"):
        self.protocol: str = protocol
        self.host: str = host
        self.port: int = port

    @property
    def base_url(self):
        return f"{self.protocol}://{self.host}:{self.port}"

    async def get_health_check(self) -> dict:
        url = urljoin(self.base_url, self.ENDPOINT_MANTLE_STATUS)
        response = requests.get(url, timeout=60)
        return response.json()

    async def get_transactions(self) -> list:
        url = urljoin(self.base_url, self.ENDPOINT_MANTLE_TRANSACTIONS)
        response = requests.get(url, timeout=60)
        return response.json()

    async def get_blocks(self) -> list:
        url = urljoin(self.base_url, self.ENDPOINT_MANTLE_BLOCKS)
        response = requests.get(url, timeout=60)
        return response.json()
