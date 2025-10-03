import random


def random_hex(length: int) -> str:
    return f"0x{random.getrandbits(length * 4):0{length}x}"


def random_hash() -> str:
    return random_hex(64)


def random_address() -> str:
    return random_hex(40)
