from core.models import NbeSchema
from core.types import HexBytes


class Note(NbeSchema):
    value: int
    public_key: HexBytes
