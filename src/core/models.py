from abc import ABC, abstractmethod
from datetime import datetime
from json import loads
from typing import Any, Optional, Self

from pydantic import BaseModel
from pydantic.config import ExtraValues
from sqlalchemy import DateTime, func
from sqlmodel import Field, SQLModel

# --- Generic ---


class NdjsonMixin(ABC):
    @abstractmethod
    def _dump_json(self) -> str:
        pass

    def model_dump_ndjson(self) -> bytes:
        return f"{self._dump_json()}\n".encode("utf-8")


# --- Pydantic ---


class NbeSchema(NdjsonMixin, BaseModel):
    def _dump_json(self) -> str:
        return self.model_dump_json()


class NbeSerializer(NbeSchema):
    pass


# --- SQLModel ---


class NbeModel(NdjsonMixin, SQLModel):
    def _dump_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def model_validate_json(
        cls,
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        extra: ExtraValues | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        """
        Sourced from: https://github.com/fastapi/sqlmodel/discussions/852
        Related:
          - https://github.com/fastapi/sqlmodel/issues/453
          - https://github.com/fastapi/sqlmodel/discussions/961

        SQLModel's `model_validate_json` is broken on `table=True`, when using JSON columns linked to a Pydantic model.
        Nested fields defined this way are transformed to plain dict/list instead of their respective Pydantic models.
        Because `model_validate` has its behaviour fixed, we delegate to it.

        Note: `pydantic.TypeAdapter` also suffers from this issue.
        """
        python_data = loads(json_data)
        return cls.model_validate(obj=python_data, strict=strict, context=context)


class IdMixin:
    id: Optional[int] = Field(default=None, primary_key=True)


class TimestampedMixin:
    created_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore[arg-type]
        sa_column_kwargs={"server_default": func.now(), "nullable": False},
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore[arg-type]
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now(), "nullable": False},
    )


class IdNbeModel(NbeModel, IdMixin):
    pass


class TimestampedModel(IdNbeModel, TimestampedMixin):
    pass
