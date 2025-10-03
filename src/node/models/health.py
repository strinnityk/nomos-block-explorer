from core.models import IdNbeModel


class Health(IdNbeModel):
    healthy: bool

    @classmethod
    def from_healthy(cls) -> "Health":
        return cls(healthy=True)

    @classmethod
    def from_unhealthy(cls) -> "Health":
        return cls(healthy=False)
