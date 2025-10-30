from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, PlainSerializer


def hexify(data: bytes) -> str:
    return data.hex()


HexBytes = Annotated[
    bytes,
    PlainSerializer(hexify, return_type=str, when_used="json"),
]
