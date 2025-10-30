from core.models import NbeSchema


class Health(NbeSchema):
    healthy: bool

    def __str__(self):
        return "Healthy" if self.healthy else "Unhealthy"

    def __repr__(self):
        return f"<Health(healthy={self.healthy})>"
