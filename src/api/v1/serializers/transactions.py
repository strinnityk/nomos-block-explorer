from typing import List, Self

from core.models import NbeSchema
from node.models.transactions import Gas, LedgerTransaction, Transaction


class TransactionRead(NbeSchema):
    id: int
    block_id: int
    operations: List[str]
    ledger_transaction: LedgerTransaction
    execution_gas_price: Gas
    storage_gas_price: Gas

    @classmethod
    def from_transaction(cls, transaction: Transaction) -> Self:
        return cls(
            id=transaction.id,
            block_id=transaction.block_id,
            operations=transaction.operations,
            ledger_transaction=transaction.ledger_transaction,
            execution_gas_price=transaction.execution_gas_price,
            storage_gas_price=transaction.storage_gas_price,
        )
