import logging
from os import getenv
from random import randint
from typing import List, Self

from rusty_results import Empty, Option

from core.models import NbeSerializer
from models.block import Block
from node.api.serializers.header import HeaderSerializer
from node.api.serializers.signed_transaction import SignedTransactionSerializer
from utils.protocols import FromRandom


def _should_randomize_transactions():
    is_debug = getenv("DEBUG", "False").lower() == "true"
    is_debug__randomize_transactions = getenv("DEBUG__RANDOMIZE_TRANSACTIONS", "False").lower() == "true"
    return is_debug and is_debug__randomize_transactions


def _get_random_transactions() -> List[SignedTransactionSerializer]:
    n = 1 if randint(0, 1) <= 0.5 else randint(2, 5)
    return [SignedTransactionSerializer.from_random() for _ in range(n)]


logger = logging.getLogger(__name__)


class BlockSerializer(NbeSerializer, FromRandom):
    header: HeaderSerializer
    transactions: List[SignedTransactionSerializer]

    @classmethod
    def model_validate_json(cls, *args, **kwargs) -> Self:
        self = super().model_validate_json(*args, **kwargs)
        if _should_randomize_transactions():
            logger.debug("DEBUG and DEBUG__RANDOMIZE_TRANSACTIONS are enabled, randomizing Block's transactions.")
            self.transactions = _get_random_transactions()
        return self

    def into_block(self) -> Block:
        transactions = [transaction.into_transaction() for transaction in self.transactions]
        return Block.model_validate(
            {
                "hash": self.header.hash,
                "parent_block": self.header.parent_block,
                "slot": self.header.slot,
                "block_root": self.header.block_root,
                "proof_of_leadership": self.header.proof_of_leadership.into_proof_of_leadership(),
            }
        ).with_transactions(transactions)

    @classmethod
    def from_random(cls, *, slot: Option[int] = None) -> Self:
        slot = slot or Empty()
        transactions = _get_random_transactions()
        return cls.model_validate({"header": HeaderSerializer.from_random(slot=slot), "transactions": transactions})

    def __str__(self) -> str:
        return f"BlockSerializer(slot={self.header.slot})"

    def __repr__(self) -> str:
        return f"<BlockSerializer(slot={self.header.slot}, hash={self.header.hash.hex()})>"
