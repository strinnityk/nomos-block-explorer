import random
from datetime import datetime
from typing import Optional

from sqlmodel import Field

from core.models import IdNbeModel
from utils.random import random_address, random_hash


class Transaction(IdNbeModel, table=True):
    __tablename__ = "transactions"

    hash: str
    block_hash: Optional[str] = Field(default=None, index=True)
    sender: str
    recipient: str
    amount: float
    timestamp: datetime = Field(default=None, index=True)

    @classmethod
    def from_random(cls) -> "Transaction":
        return Transaction(
            hash=random_hash(),
            block_hash=random_hash(),
            sender=random_address(),
            recipient=random_address(),
            amount=round(random.uniform(0.0001, 100.0), 6),
            timestamp=datetime.now(),
        )
