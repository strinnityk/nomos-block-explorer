import logging
import os
import random
from typing import TYPE_CHECKING, Any, List, Self

from pydantic.config import ExtraValues
from pydantic_core.core_schema import computed_field
from sqlalchemy import Column
from sqlmodel import Field, Relationship

from core.models import NbeSchema, TimestampedModel
from core.sqlmodel import PydanticJsonColumn
from utils.random import random_hash

if TYPE_CHECKING:
    from node.models.transactions import Transaction


def _is_debug__randomize_transactions():
    is_debug = os.getenv("DEBUG", "False").lower() == "true"
    is_debug__randomize_transactions = os.getenv("DEBUG__RANDOMIZE_TRANSACTIONS", "False").lower() == "true"
    return is_debug and is_debug__randomize_transactions


logger = logging.getLogger(__name__)


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
    __tablename__ = "block"

    header: Header = Field(sa_column=Column(PydanticJsonColumn(Header), nullable=False))
    transactions: List["Transaction"] = Relationship(
        back_populates="block",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan",
        },
    )

    @property
    def slot(self) -> int:
        return self.header.slot

    def __str__(self) -> str:
        return f"Block(slot={self.slot})"

    def __repr__(self) -> str:
        return f"<Block(id={self.id}, created_at={self.created_at}, slot={self.slot}, parent={self.header["parent_block"]})>"

    @classmethod
    def model_validate_json(
        cls,
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        extra: ExtraValues | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        self = super().model_validate_json(
            json_data, strict=strict, extra=extra, context=context, by_alias=by_alias, by_name=by_name
        )
        if _is_debug__randomize_transactions():
            from node.models.transactions import Transaction

            logger.debug("DEBUG and DEBUG__RANDOMIZE_TRANSACTIONS is enabled, randomizing Block's transactions.")
            n = 0 if random.randint(0, 1) <= 0.5 else random.randint(1, 10)
            self.transactions = [Transaction.from_random() for _ in range(n)]
        return self

    @classmethod
    def from_random(cls, slot_from: int = 1, slot_to: int = 100) -> "Block":
        n = 0 if random.randint(0, 1) < 0.3 else random.randint(1, 5)
        transactions = [Transaction.from_random() for _ in range(n)]
        return Block(
            header=Header.from_random(slot_from, slot_to),
            transactions=transactions,
        )
