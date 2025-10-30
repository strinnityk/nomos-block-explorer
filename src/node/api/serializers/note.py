from random import randint
from typing import Self

from pydantic import Field

from core.models import NbeSerializer
from models.transactions.notes import Note
from node.api.serializers.fields import BytesFromHex
from utils.protocols import FromRandom
from utils.random import random_bytes


class NoteSerializer(NbeSerializer, FromRandom):
    value: int = Field(description="Integer in u64 format.")
    public_key: BytesFromHex = Field(alias="pk", description="Fr integer.")

    def into_note(self) -> Note:
        return Note.model_validate(
            {
                "value": self.value,
                "public_key": self.public_key,
            }
        )

    @classmethod
    def from_random(cls) -> Self:
        return cls.model_validate({"value": randint(1, 100), "pk": random_bytes(32).hex()})
