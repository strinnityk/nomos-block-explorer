from random import randint
from typing import Self

from pydantic import Field
from rusty_results import Option

from core.models import NbeSerializer
from models.header.public import Public
from node.api.serializers.fields import BytesFromHex
from utils.protocols import FromRandom
from utils.random import random_bytes


class PublicSerializer(NbeSerializer, FromRandom):
    aged_root: BytesFromHex = Field(description="Fr integer in hex format.")
    epoch_nonce: BytesFromHex = Field(description="Fr integer in hex format.")
    latest_root: BytesFromHex = Field(description="Fr integer in hex format.")
    slot: int = Field(description="Integer in u64 format.")
    total_stake: int = Field(description="Integer in u64 format.")

    def into_public(self) -> Public:
        return Public.model_validate(
            {
                "aged_root": self.aged_root,
                "epoch_nonce": self.epoch_nonce,
                "latest_root": self.latest_root,
                "slot": self.slot,
                "total_stake": self.total_stake,
            }
        )

    @classmethod
    def from_random(cls, slot: Option[int]) -> Self:
        cls.model_validate(
            {
                "aged_root": random_bytes(32).hex(),
                "epoch_nonce": random_bytes(32).hex(),
                "latest_root": random_bytes(32).hex(),
                "slot": slot.unwrap_or(randint(0, 10_000)),
                "total_stake": randint(0, 10_000),
            }
        )
