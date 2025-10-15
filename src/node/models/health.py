from core.models import IdNbeModel


class Health(IdNbeModel):
    healthy: bool

    @classmethod
    def from_healthy(cls) -> "Health":
        return cls(healthy=True)

    @classmethod
    def from_unhealthy(cls) -> "Health":
        return cls(healthy=False)

    def __str__(self):
        return "Healthy" if self.healthy else "Unhealthy"

    def __repr__(self):
        return f"<Health(healthy={self.healthy})>"
