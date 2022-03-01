import os
import pathlib
import typing

StrOrPath = str | pathlib.Path


class EnvironError(Exception):
    pass


class ConfigError(Exception):
    def __init__(self, *exceptions: Exception) -> None:
        self._exceptions = list(exceptions)

    def append(self, exc: Exception):
        self._exceptions.append(exc)

    def __bool__(self):
        return bool(self._exceptions)

    def __str__(self) -> str:
        return 'ConfigError raised from the following errors(\n{errors}\n)'.format(
            errors='\n'.join(map(str, self._exceptions))
        )

    def __repr__(self) -> str:
        return '\n' + '\n'.join(map(repr, self._exceptions))


MISSING = object()
T = typing.TypeVar('T')
CastType = type | typing.Callable[[typing.Any], typing.Any]


class Environ(typing.MutableMapping):
    def __init__(
        self, env_mapping: typing.MutableMapping | None = None
    ) -> None:
        self._environ = env_mapping if env_mapping is not None else os.environ
        self._has_been_read = set[typing.Any]()

    def __getitem__(self, key: typing.Any) -> typing.Any:
        self._has_been_read.add(key)
        return self._environ.__getitem__(key)

    def __setitem__(self, key: str, value: typing.Any) -> None:
        if key in self._has_been_read:
            raise EnvironError(
                f'Attempting to set environ["{key}"], but the value has already been read.'
            )
        self._environ.__setitem__(key, value)

    def __delitem__(self, key: typing.Any) -> None:
        if key in self._has_been_read:
            raise EnvironError(
                f'Attempting to set environ["{key}"], but the value has already been read.'
            )
        self._environ.__delitem__(key)

    def __iter__(self):
        return iter(self._environ)

    def __len__(self) -> int:
        return len(self._environ)


environ = Environ()


def _read_file(env_file: StrOrPath):
    output = {}
    with open(env_file, encoding='locale') as stream:
        for line in stream:
            if line.startswith('#') or '=' not in line:
                continue
            name, value = line.split('=', 1)
            output[name.strip()] = value.strip()
    return output


def _cast(name: str, value: typing.Any, cast: CastType) -> typing.Any:
    try:
        return cast(value)
    except (TypeError, ValueError) as err:
        raise ValueError(
            f'Config "{name}" has value "{value}". Not a valid {cast.__name__}'
        ) from err


class Config:
    def __init__(
        self,
        env_file: StrOrPath | None = None,
        environ: typing.Mapping[str, str] = environ,
        group_exceptions: bool = True,
    ) -> None:  # pylint: disable=redefining-outer-name
        self._environ = environ
        self._file_vals = dict[str, str]()
        self._group_exceptions = group_exceptions
        self._errors = ConfigError()
        if env_file is not None and os.path.isfile(env_file):
            self._file_vals = _read_file(env_file)

    def _get_value(self, name: str, default: typing.Any) -> str:
        value = self._environ.get(name, self._file_vals.get(name, default))
        if value is MISSING:
            raise KeyError(f'Config "{name}" is missing and has no default. ')
        return value

    def get(
        self,
        name: str,
        cast: CastType | None = None,
        default: typing.Any = MISSING,
    ) -> typing.Any:
        try:
            val = self._get(name, cast, default)
        except Exception as err:
            if not self._group_exceptions:
                raise
            self._errors.append(err)
        else:
            return val

    def _get(
        self,
        name: str,
        cast: CastType | None = None,
        default: typing.Any = MISSING,
    ) -> typing.Any:

        value = self._get_value(name, default)
        if cast is None:
            return value
        return _cast(name, value, cast)

    @typing.overload
    def __call__(
        self,
        name: str,
        cast: typing.Callable[[str | T], T],
        default: str | T = MISSING,
    ) -> T:
        ...

    @typing.overload
    def __call__(
        self, name: str, cast: type[T], default: str | T = MISSING
    ) -> T:
        ...

    @typing.overload
    def __call__(
        self, name: str, cast: None = None, default: str | object = MISSING
    ) -> str:
        ...

    def __call__(
        self,
        name: str,
        cast: typing.Callable | type | None = None,
        default: typing.Any = MISSING,
    ) -> typing.Any:
        return self.get(name, cast, default)

    def raise_on_error(self):
        if self._errors:
            raise self._errors
