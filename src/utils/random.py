import random
from typing import List


def random_bytes(length: int) -> bytes:
    return bytes((random.randint(0, 255) for _ in range(length)))


def random_address() -> bytes:
    return random_bytes(40)


def random_hash() -> bytes:
    return random_bytes(64)


def as_list(data: bytes) -> List[int]:
    return list(data)
