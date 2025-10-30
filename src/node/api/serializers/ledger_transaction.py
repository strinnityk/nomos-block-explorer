from random import randint
from typing import List, Self

from pydantic import Field

from core.models import NbeSerializer
from node.api.serializers.fields import BytesFromIntArray
from node.api.serializers.note import NoteSerializer
from utils.protocols import FromRandom
from utils.random import random_bytes


class LedgerTransactionSerializer(NbeSerializer, FromRandom):
    inputs: List[BytesFromIntArray] = Field(description="Fr integer.")
    outputs: List[NoteSerializer]

    @classmethod
    def from_random(cls) -> Self:
        n_inputs = 0 if randint(0, 1) <= 0.5 else randint(1, 5)
        n_outputs = 0 if randint(0, 1) <= 0.5 else randint(1, 5)

        return cls.model_validate(
            {
                "inputs": [list(random_bytes(2048)) for _ in range(n_inputs)],
                "outputs": [NoteSerializer.from_random() for _ in range(n_outputs)],
            }
        )
