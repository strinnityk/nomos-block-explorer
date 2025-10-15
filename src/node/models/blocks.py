import random
from typing import List

from sqlalchemy import Column
from sqlmodel import Field

from core.models import NbeSchema, TimestampedModel
from core.sqlmodel import PydanticJsonColumn
from node.models.transactions import Transaction
from utils.random import random_hash


class Public(NbeSchema):
    aged_root: str
    epoch_nonce: str
    latest_root: str
    slot: int
    total_stake: float

    @classmethod
    def from_random(cls, slot: int = None) -> "Public":
        if slot is not None:
            slot = random.randint(1, 100)

        return Public(
            aged_root=random_hash(),
            epoch_nonce=random_hash(),
            latest_root=random_hash(),
            slot=slot,
            total_stake=100.0,
        )


class ProofOfLeadership(NbeSchema):
    entropy_contribution: str
    leader_key: List[int]
    proof: List[int]
    public: Public
    voucher_cm: str

    @classmethod
    def from_random(cls, slot: int = None) -> "ProofOfLeadership":
        random_hash_as_list = lambda: [random.randint(0, 255) for _ in range(64)]

        return ProofOfLeadership(
            entropy_contribution=random_hash(),
            leader_key=random_hash_as_list(),
            proof=random_hash_as_list(),
            public=Public.from_random(slot),
            voucher_cm=random_hash(),
        )


class Header(NbeSchema):
    block_root: str
    parent_block: str
    proof_of_leadership: ProofOfLeadership
    slot: int

    @classmethod
    def from_random(cls, slot_from: int = 1, slot_to: int = 100) -> "Header":
        slot = random.randint(slot_from, slot_to)
        return Header(
            block_root=random_hash(),
            parent_block=random_hash(),
            proof_of_leadership=ProofOfLeadership.from_random(slot),
            slot=slot,
        )


class Block(TimestampedModel, table=True):
    __tablename__ = "blocks"

    header: Header = Field(sa_column=Column(PydanticJsonColumn(Header), nullable=False))
    transactions: List[Transaction] = Field(
        default_factory=list, sa_column=Column(PydanticJsonColumn(Transaction, many=True), nullable=False)
    )

    @property
    def slot(self) -> int:
        return self.header.slot

    def __str__(self) -> str:
        return f"Block(slot={self.slot})"

    def __repr__(self) -> str:
        return f"<Block(id={self.id}, created_at={self.created_at}, slot={self.slot}, parent={self.header['parent_block']})>"

    @classmethod
    def from_random(cls, slot_from: int = 1, slot_to: int = 100) -> "Block":
        n = random.randint(1, 10)
        _transactions = [Transaction.from_random() for _ in range(n)]
        return Block(
            header=Header.from_random(slot_from, slot_to),
            transactions=[],
        )
