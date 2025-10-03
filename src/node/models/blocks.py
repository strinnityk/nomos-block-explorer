from datetime import datetime

from sqlmodel import Field

from core.models import IdNbeModel
from utils.random import random_hash


class Block(IdNbeModel, table=True):
    __tablename__ = "blocks"

    slot: int
    hash: str
    parent_hash: str
    transaction_count: int
    timestamp: datetime = Field(default=None, index=True)

    @classmethod
    def from_random(cls, slot_start=1, slot_end=10_000) -> "Block":
        import random

        return cls(
            slot=random.randint(slot_start, slot_end),
            hash=random_hash(),
            parent_hash=random_hash(),
            transaction_count=random.randint(0, 500),
            timestamp=datetime.now(),
        )
