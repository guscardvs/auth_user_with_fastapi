import uuid
from typing import Any

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.types import String, TypeDecorator

DEFAULT_UUID_LENGTH = 32


class GUID(TypeDecorator):   # pylint: disable=abstract-method
    impl = String
    cache_ok = True

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault('length', DEFAULT_UUID_LENGTH)
        super().__init__(*args, **kwargs)

    def load_dialect_impl(self, dialect: Dialect) -> 'TypeEngine[Any]':
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID)
        return dialect.type_descriptor(String)

    def process_bind_param(self, value: Any, dialect: Dialect) -> Any:
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return f'%.{DEFAULT_UUID_LENGTH}x' % (value.int)

    def process_result_value(self, value: Any, dialect: Dialect) -> Any | None:
        if value is not None and not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value
