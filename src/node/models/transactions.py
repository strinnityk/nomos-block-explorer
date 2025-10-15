import random
from enum import StrEnum
from typing import List

from sqlalchemy import JSON, Column
from sqlmodel import Field

from core.models import NbeSchema, TimestampedModel
from utils.random import random_address

Value = int
Fr = int
Gas = float
PublicKey = bytes


class Operation(StrEnum):
    CHANNEL_INSCRIBE = ("ChannelInscribe",)  # (InscriptionOp)
    CHANNEL_BLOB = ("ChannelBlob",)  # (BlobOp)
    CHANNEL_SET_KEYS = ("ChannelSetKeys",)  # (SetKeysOp)
    NATIVE = ("Native",)  # (NativeOp)
    SDP_DECLARE = ("SDPDeclare",)  # (SDPDeclareOp)
    SDP_WITHDRAW = ("SDPWithdraw",)  # (SDPWithdrawOp)
    SDP_ACTIVE = ("SDPActive",)  # (SDPActiveOp)
    LEADER_CLAIM = ("LeaderClaim",)  # (LeaderClaimOp)


class Note(NbeSchema):
    value: Value
    public_key: PublicKey

    @classmethod
    def from_random(cls) -> "Note":
        return Note(
            value=random.randint(1, 100),
            public_key=random_address(),
        )


class LedgerTransaction(NbeSchema):
    """
    Tx
    """

    inputs: List[Fr] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    outputs: List[Note] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))

    @classmethod
    def from_random(cls) -> "LedgerTransaction":
        return LedgerTransaction(
            inputs=[random.randint(1, 100) for _ in range(10)],
            outputs=[Note.from_random() for _ in range(10)],
        )


class Transaction(NbeSchema):  # table=true # It currently lives inside Block
    """
    MantleTx
    """

    # __tablename__ = "transactions"

    # TODO: hash
    operations: List[str] = Field(alias="ops", default_factory=list, sa_column=Column(JSON, nullable=False))
    ledger_transaction: LedgerTransaction = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    execution_gas_price: Gas
    storage_gas_price: Gas

    def __str__(self) -> str:
        return f"Transaction({self.operations})"

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, created_at={self.created_at}, operations={self.operations})>"

    @classmethod
    def from_random(cls) -> "Transaction":
        n = random.randint(1, 10)
        operations = [random.choice(list(Operation)).value for _ in range(n)]
        return Transaction(
            operations=operations,
            ledger_transaction=LedgerTransaction.from_random(),
            execution_gas_price=random.random(),
            storage_gas_price=random.random(),
        )
