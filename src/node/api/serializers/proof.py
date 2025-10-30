from abc import ABC, abstractmethod
from typing import Annotated, Self, Union

from pydantic import Field, RootModel

from core.models import NbeSerializer
from models.transactions.operations.proofs import (
    Ed25519Signature,
    NbeSignature,
    ZkAndEd25519Signature,
    ZkSignature,
)
from node.api.serializers.fields import BytesFromHex
from utils.protocols import EnforceSubclassFromRandom
from utils.random import random_bytes


class OperationProofSerializer(EnforceSubclassFromRandom, ABC):
    @abstractmethod
    def into_operation_proof(cls) -> NbeSignature:
        raise NotImplementedError


# TODO: Differentiate between Ed25519SignatureSerializer and ZkSignatureSerializer


class Ed25519SignatureSerializer(OperationProofSerializer, RootModel[str]):
    root: BytesFromHex

    def into_operation_proof(self) -> NbeSignature:
        return Ed25519Signature.model_validate(
            {
                "signature": self.root,
            }
        )

    @classmethod
    def from_random(cls, *args, **kwargs) -> Self:
        return cls.model_validate(random_bytes(64).hex())


class ZkSignatureSerializer(OperationProofSerializer, RootModel[str]):
    root: BytesFromHex

    def into_operation_proof(self) -> NbeSignature:
        return ZkSignature.model_validate(
            {
                "signature": self.root,
            }
        )

    @classmethod
    def from_random(cls, *args, **kwargs) -> Self:
        return cls.model_validate(random_bytes(32).hex())


class ZkAndEd25519SignaturesSerializer(OperationProofSerializer, NbeSerializer):
    zk_signature: BytesFromHex = Field(alias="zk_sig")
    ed25519_signature: BytesFromHex = Field(alias="ed25519_sig")

    def into_operation_proof(self) -> NbeSignature:
        return ZkAndEd25519Signature.model_validate(
            {
                "zk_signature": self.zk_signature,
                "ed25519_signature": self.ed25519_signature,
            }
        )

    @classmethod
    def from_random(cls, *args, **kwargs) -> Self:
        return ZkAndEd25519SignaturesSerializer.model_validate(
            {
                "zk_sig": random_bytes(32).hex(),
                "ed25519_sig": random_bytes(32).hex(),
            }
        )


OperationProofSerializerVariants = Union[
    Ed25519SignatureSerializer, ZkSignatureSerializer, ZkAndEd25519SignaturesSerializer
]
OperationProofSerializerField = Annotated[OperationProofSerializerVariants, Field(union_mode="left_to_right")]
