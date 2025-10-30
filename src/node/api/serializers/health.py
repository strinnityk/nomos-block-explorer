from typing import Any, Self

from core.models import NbeSerializer
from models.health import Health


class HealthSerializer(NbeSerializer):
    is_healthy: bool

    def into_health(self) -> Health:
        return Health.model_validate({"healthy": self.is_healthy})

    @classmethod
    def from_healthy(cls) -> Self:
        return cls.model_validate({"is_healthy": True})

    @classmethod
    def from_unhealthy(cls) -> Self:
        return cls.model_validate({"is_healthy": False})
