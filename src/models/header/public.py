from core.models import NbeSchema
from core.types import HexBytes


class Public(NbeSchema):
    aged_root: HexBytes
    epoch_nonce: HexBytes
    latest_root: HexBytes
    slot: int
    total_stake: int
