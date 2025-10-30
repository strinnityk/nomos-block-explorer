from typing import Annotated

from pydantic import BeforeValidator, PlainSerializer, ValidationError


def bytes_from_intarray(data: list[int]) -> bytes:
    if not isinstance(data, list):
        raise ValueError(f"Unsupported data type for bytes deserialization. Expected list, got {type(data).__name__}.")
    elif not all(isinstance(item, int) for item in data):
        raise ValueError("List items must be integers.")
    else:
        return bytes(data)


def bytes_from_hex(data: str) -> bytes:
    if not isinstance(data, str):
        raise ValueError(
            f"Unsupported data type for bytes deserialization. Expected string, got {type(data).__name__}."
        )
    return bytes.fromhex(data)


def bytes_from_int(data: int) -> bytes:
    if not isinstance(data, int):
        raise ValueError(
            f"Unsupported data type for bytes deserialization. Expected integer, got {type(data).__name__}."
        )
    return data.to_bytes((data.bit_length() + 7) // 8)  # TODO: Ensure endianness is correct.


def bytes_into_hex(data: bytes) -> str:
    return data.hex()


BytesFromIntArray = Annotated[bytes, BeforeValidator(bytes_from_intarray), PlainSerializer(bytes_into_hex)]
BytesFromHex = Annotated[bytes, BeforeValidator(bytes_from_hex), PlainSerializer(bytes_into_hex)]
BytesFromInt = Annotated[bytes, BeforeValidator(bytes_from_int), PlainSerializer(bytes_into_hex)]
