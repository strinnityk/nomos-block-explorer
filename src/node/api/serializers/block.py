from random import randint
from typing import List, Self

from rusty_results import Empty, Option

from core.models import NbeSerializer
from models.block import Block
from node.api.serializers.header import HeaderSerializer
from node.api.serializers.signed_transaction import SignedTransactionSerializer
from utils.protocols import FromRandom


class BlockSerializer(NbeSerializer, FromRandom):
    header: HeaderSerializer
    transactions: List[SignedTransactionSerializer]

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
        n = 1 if randint(0, 1) <= 0.5 else randint(2, 5)
        transactions = [SignedTransactionSerializer.from_random() for _ in range(n)]
        return cls.model_validate({"header": HeaderSerializer.from_random(slot=slot), "transactions": transactions})
