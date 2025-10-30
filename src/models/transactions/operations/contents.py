from enum import Enum
from typing import List, Optional

from core.models import NbeSchema
from core.types import HexBytes


class ContentType(Enum):
    CHANNEL_INSCRIBE = "ChannelInscribe"
    CHANNEL_BLOB = "ChannelBlob"
    CHANNEL_SET_KEYS = "ChannelSetKeys"
    SDP_DECLARE = "SDPDeclare"
    SDP_WITHDRAW = "SDPWithdraw"
    SDP_ACTIVE = "SDPActive"
    LEADER_CLAIM = "LeaderClaim"


class NbeContent(NbeSchema):
    type: ContentType


class ChannelInscribe(NbeContent):
    type: ContentType = ContentType.CHANNEL_INSCRIBE
    channel_id: HexBytes
    inscription: HexBytes
    parent: HexBytes
    signer: HexBytes


class ChannelBlob(NbeContent):
    type: ContentType = ContentType.CHANNEL_BLOB
    channel: HexBytes
    blob: HexBytes
    blob_size: int
    da_storage_gas_price: int
    parent: HexBytes
    signer: HexBytes


class ChannelSetKeys(NbeContent):
    type: ContentType = ContentType.CHANNEL_SET_KEYS
    channel: HexBytes
    keys: List[bytes]


class SDPDeclareServiceType(Enum):
    BN = "BN"
    DA = "DA"


class SDPDeclare(NbeContent):
    type: ContentType = ContentType.SDP_DECLARE
    service_type: SDPDeclareServiceType
    locators: List[bytes]
    provider_id: HexBytes
    zk_id: HexBytes
    locked_note_id: HexBytes


class SDPWithdraw(NbeContent):
    type: ContentType = ContentType.SDP_WITHDRAW
    declaration_id: HexBytes
    nonce: HexBytes


class SDPActive(NbeContent):
    type: ContentType = ContentType.SDP_ACTIVE
    declaration_id: HexBytes
    nonce: HexBytes
    metadata: Optional[bytes]


class LeaderClaim(NbeContent):
    type: ContentType = ContentType.LEADER_CLAIM
    rewards_root: HexBytes
    voucher_nullifier: HexBytes
    mantle_tx_hash: HexBytes


OperationContent = ChannelInscribe | ChannelBlob | ChannelSetKeys | SDPDeclare | SDPWithdraw | SDPActive | LeaderClaim
