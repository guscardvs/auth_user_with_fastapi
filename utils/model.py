import re
from typing import Any, TypeVar

import orjson
import pydantic

TO_CAMEL_REGEXP = re.compile(r'_([a-zA-Z0-9])')
ModelT = TypeVar('ModelT', bound=pydantic.BaseModel)


def orjson_dumps(v, *, default: Any = None):
    return orjson.dumps(v, default=default).decode()


class Model(pydantic.BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

        frozen = True

        allow_population_by_field_name = True

        @classmethod
        def alias_generator(cls, field: str):
            return re.sub(
                TO_CAMEL_REGEXP,
                lambda match: match[1].upper(),
                field.removesuffix('_'),
            )


def get_optional_model(model: type[ModelT], *exclude: str) -> type[ModelT]:
    edit_dto = pydantic.create_model(
        f'Optional{model.__name__}',
        __base__=model,
        __module__=model.__module__,
    )
    for field in edit_dto.__fields__.values():
        field.required = False
        field.allow_none = True
        field.default = None
    for field in exclude:
        edit_dto.__fields__.pop(field)
    return edit_dto
