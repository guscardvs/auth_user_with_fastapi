import http
from typing import NamedTuple, final


class _Response(NamedTuple):
    message: str
    status_code: int


def _append_exclamation_mark(message: str):
    return message if message.endswith('!') else f'{message}!'


class APIError(Exception):
    _status = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str) -> None:
        self._message = message

    @final
    def get_message(self):
        return _append_exclamation_mark(self._message)

    @final
    def response(self) -> _Response:
        return _Response(self.get_message(), self._status)


class DatabaseError(Exception):
    _status = http.HTTPStatus.BAD_REQUEST

    def __init__(self, target: str) -> None:
        self._target = target

    def get_message(self):
        return f'An error occured with {self._target}'

    @final
    def _get_message(self):
        return _append_exclamation_mark(self.get_message())

    @final
    def response(self) -> _Response:
        return _Response(self._get_message(), self._status)


class NotFoundError(DatabaseError):
    _status = http.HTTPStatus.NOT_FOUND

    def get_message(self):
        return f'{self._target} not found'


class ConflictError(DatabaseError):
    _status = http.HTTPStatus.CONFLICT

    def get_message(self):
        return f'{self._target} already exists'


class ForbiddenError(APIError):
    _status = http.HTTPStatus.FORBIDDEN

    def __init__(self) -> None:
        super().__init__('You do not have permission to use this route')


class InvalidPassword(ForbiddenError):
    def __init__(self) -> None:
        self._message = 'Invalid Password'


class UnsetPassword(APIError):
    def __init__(self) -> None:
        super().__init__('User has not set password yet')


class NotAuthenticated(APIError):
    _status = http.HTTPStatus.UNAUTHORIZED

    def __init__(self) -> None:
        self._message = 'not authenticated'


class InvalidOrExpiredToken(NotAuthenticated):
    def __init__(self) -> None:
        self._message = 'Invalid or expired token'
