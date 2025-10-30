from enum import Enum

from core.models import NbeSchema
from core.types import HexBytes


class SignatureType(Enum):
    ED25519 = "Ed25519"
    ZK = "Zk"
    ZK_AND_ED25519 = "ZkAndEd25519"


class NbeSignature(NbeSchema):
    type: SignatureType


class Ed25519Signature(NbeSignature):
    type: SignatureType = SignatureType.ED25519
    signature: HexBytes


class ZkSignature(NbeSignature):
    type: SignatureType = SignatureType.ZK
    signature: HexBytes


class ZkAndEd25519Signature(NbeSignature):
    type: SignatureType = SignatureType.ZK_AND_ED25519
    zk_signature: HexBytes
    ed25519_signature: HexBytes


OperationProof = Ed25519Signature | ZkSignature | ZkAndEd25519Signature
