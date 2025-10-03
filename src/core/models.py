from typing import Optional

from sqlmodel import Field, SQLModel


class NbeModel(SQLModel):
    def model_dump_ndjson(self) -> bytes:
        return f"{self.model_dump_json()}\n".encode("utf-8")


class IdNbeModel(NbeModel):
    id: Optional[int] = Field(default=None, primary_key=True)
