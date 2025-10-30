import logging
import os
import random
from typing import TYPE_CHECKING, Any, List, Self

from pydantic.config import ExtraValues
from sqlalchemy import Column
from sqlmodel import Field, Relationship

from core.models import TimestampedModel
from core.sqlmodel import PydanticJsonColumn
from core.types import HexBytes
from models.header.proof_of_leadership import ProofOfLeadership

if TYPE_CHECKING:
    from models.transactions.transaction import Transaction


logger = logging.getLogger(__name__)


def _should_randomize_transactions():
    is_debug = os.getenv("DEBUG", "False").lower() == "true"
    is_debug__randomize_transactions = os.getenv("DEBUG__RANDOMIZE_TRANSACTIONS", "False").lower() == "true"
    return is_debug and is_debug__randomize_transactions


class Block(TimestampedModel, table=True):
    __tablename__ = "block"

    # --- Columns --- #

    hash: HexBytes = Field(nullable=False, unique=True)
    parent_block: HexBytes = Field(nullable=False)
    slot: int = Field(nullable=False)
    block_root: HexBytes = Field(nullable=False)
    proof_of_leadership: ProofOfLeadership = Field(
        sa_column=Column(PydanticJsonColumn(ProofOfLeadership), nullable=False)
    )

    # --- Relationships --- #

    transactions: List["Transaction"] = Relationship(
        back_populates="block",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __str__(self) -> str:
        return f"Block(slot={self.slot})"

    def __repr__(self) -> str:
        return f"<Block(id={self.id}, created_at={self.created_at}, slot={self.slot}, parent={self.header["parent_block"]})>"

    def with_transactions(self, transactions: List["Transaction"]) -> Self:
        self.transactions = transactions
        return self

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
        if _should_randomize_transactions():
            from models.transactions.transaction import Transaction

            logger.debug("DEBUG and DEBUG__RANDOMIZE_TRANSACTIONS are enabled, randomizing Block's transactions.")
            n_transactions = 0 if random.randint(0, 1) <= 0.3 else random.randint(1, 5)
            self.transactions = [Transaction.from_random() for _ in range(n_transactions)]
        return self
