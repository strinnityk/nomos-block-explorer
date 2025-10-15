from typing import Any, Generic, List, TypeVar

from pydantic import TypeAdapter
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON as SA_JSON, TypeDecorator

T = TypeVar("T")


class PydanticJsonColumn(TypeDecorator, Generic[T]):
    """
    Store/load a Pydantic v2 model (or list of models) in a JSON/JSONB column.

    Python -> DB: accepts Model | dict | list[Model] | list[dict] | JSON str/bytes,
      emits dict or list[dict] (what JSON columns expect).
    DB -> Python: returns Model or list[Model], preserving shape.
    """

    impl = SA_JSON
    cache_ok = True

    def __init__(self, model: type[T], *, many: bool = False) -> None:
        super().__init__()
        self.many = many
        self._ta = TypeAdapter(List[model] if many else model)

    # Use JSONB on Postgres, JSON elsewhere
    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(JSONB()) if dialect.name == "postgresql" else dialect.type_descriptor(SA_JSON())

    # Python -> DB (on INSERT/UPDATE)
    def process_bind_param(self, value: Any, _dialect) -> Any:
        if value is None:
            return [] if self.many else None

        # If given JSON text/bytes, validate from JSON; else from Python
        if isinstance(value, (str, bytes, bytearray)):
            model_value = self._ta.validate_json(value.decode() if not isinstance(value, str) else value)
        else:
            model_value = self._ta.validate_python(value)

        # Dump to plain Python (dict/list) for the JSON column
        return self._ta.dump_python(model_value, mode="json")

    # DB -> Python (on SELECT)
    def process_result_value(self, value: Any, _dialect):
        if value is None:
            return [] if self.many else None
        return self._ta.validate_python(value)
