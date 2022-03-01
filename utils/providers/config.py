import typing
from types import NoneType

from pydantic.fields import FieldInfo, ModelField, Undefined

from utils.config import MISSING, Config
from utils.model import Model


class ProviderConfig(Model):
    __env_prefix__ = ''

    @classmethod
    def _with_prefix(cls, name: str):
        return '_'.join(item for item in (cls.__env_prefix__, name) if item)

    @classmethod
    def from_env(cls, config: Config | None = None):
        if config is None:
            config = Config()
        args = {
            field.name: value
            for field in cls.__fields__.values()
            if (value := cls._get_config_value(field, config)) is not MISSING
        }
        config.raise_on_error()
        return cls(**args)

    @classmethod
    def _get_config_value(
        cls, field: ModelField, config: Config
    ) -> typing.Any:
        name = cls._with_prefix(field.name).upper()
        default = _get_default(field.field_info)
        type_ = _get_type(field.outer_type_)
        if not field.allow_none:
            return config.get(name, cast=field.type_, default=default)
        value = config.get(name, default=default)
        if not value:
            return None
        return type_(value)


def _get_default(field_info: FieldInfo):
    if field_info.default is not Undefined:
        return field_info.default
    if field_info.default_factory is not None:
        return field_info.default_factory()
    return MISSING


def _get_type(field_type: type) -> type:
    is_union = typing.get_origin(field_type) is typing.Union
    if not is_union:
        return field_type
    args = typing.get_args(field_type)
    if len(args) != 2 or args[1] is not NoneType:
        raise NotImplementedError
    return args[0]
