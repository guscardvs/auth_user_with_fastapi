import enum
from abc import abstractmethod
from typing import Callable, Protocol, TypeGuard

import sqlalchemy as sa
from fastapi import Request
from psycopg2 import errorcodes as pg_errors
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext import asyncio as async_sa
from sqlalchemy.pool import StaticPool
from starlette.datastructures import State
from typing_extensions import AsyncContextManager, Awaitable

from utils import exc
from utils.helpers import on_error
from utils.providers.config import ProviderConfig


class DriverTypes(Protocol):
    port: int
    has_config: bool
    async_driver: str
    sync_driver: str

    config = {}

    def get_connection_uri(self, is_async: bool, cfg: 'DatabaseConfig') -> str:
        """Returns autogenerated driver uri for sqlalchemy create_engine()"""
        driver_prefix = self.async_driver if is_async else self.sync_driver
        return f'{driver_prefix}://{cfg.user}:{cfg.password}@{cfg.host}:{cfg.get_port()}/{cfg.name}'

    @abstractmethod
    def is_duplicate(self, exc: IntegrityError) -> bool:
        ...


class PostgresDriver(DriverTypes):
    """Driver Default values for PostgreSQL Connection"""

    port = 5432
    async_driver = 'postgresql+asyncpg'
    sync_driver = 'postgresql+psycopg2'
    has_config = False

    def is_duplicate(self, exc: IntegrityError):
        return exc.orig.code == pg_errors.UNIQUE_VIOLATION


class SqliteDriver(DriverTypes):
    port = 0
    async_driver = 'sqlite+aiosqlite'
    sync_driver = 'sqlite'
    has_config = True

    config = {
        'connect_args': {'check_same_thread': False},
        'poolclass': StaticPool,
    }

    def get_connection_uri(self, is_async: bool, cfg: 'DatabaseConfig') -> str:
        driver_prefix = self.async_driver if is_async else self.sync_driver
        return f'{driver_prefix}:///{cfg.host}'

    def is_duplicate(self, exc: IntegrityError):
        import sqlite3

        return isinstance(exc.orig, sqlite3.IntegrityError)


class Driver(str, enum.Enum):
    POSTGRES = 'postgres'
    SQLITE = 'sqlite'


class DatabaseConfig(ProviderConfig):
    """Database configuration params
    Obs: pass filename as host if using sqlite"""

    __env_prefix__ = 'DB'

    driver: Driver
    host: str
    name: str = ''
    user: str = ''
    password: str = ''
    port: int | None = None
    _pool_size: int = 20
    _pool_recycle: int = 3600
    _max_overflow: int = 0

    def get_port(self):
        return self.port if self.port is not None else self.driver_type.port

    def get_uri(self, *, is_async: bool):
        return self.driver_type.get_connection_uri(is_async, self)

    @property
    def pool_config(self) -> dict[str, int]:
        if self.driver_type.has_config:
            return self.driver_type.config
        return {
            'pool_size': self._pool_size,
            'pool_recycle': self._pool_recycle,
            'max_overflow': self._max_overflow,
        }

    @property
    def driver_type(self) -> DriverTypes:
        _driver_mapping = {
            Driver.POSTGRES: PostgresDriver,
            Driver.SQLITE: SqliteDriver,
        }
        return _driver_mapping[self.driver]()


class ConnectionContext(AsyncContextManager):
    def __init__(
        self,
        connection_factory: Callable[[], Awaitable[async_sa.AsyncConnection]],
    ) -> None:
        self._factory = connection_factory
        self._connection: async_sa.AsyncConnection | None = None

    async def connect(self):
        if not self.is_open(self._connection):
            self._connection = await self._factory()
        return self._connection

    @staticmethod
    def is_open(
        conn: async_sa.AsyncConnection | None,
    ) -> TypeGuard[async_sa.AsyncConnection]:
        return bool(conn and not conn.closed)

    async def disconnect(self):
        if self.is_open(self._connection):
            await self._connection.close()
        self._connection = None

    async def __aenter__(self):
        return await self.connect()

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.disconnect()

    def __await__(self):
        yield self.connect().__await__()
        return self


class DatabaseProvider:
    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config
        self._engine = async_sa.create_async_engine(
            self._config.get_uri(is_async=True), **self._config.pool_config
        )

    def acquire(self):
        return ConnectionContext(self._engine.connect)

    @on_error(Exception, exc.DatabaseError, target='database')
    async def health_check(self):
        async with self.acquire() as conn:
            await conn.execute(sa.text('SELECT 1'))
        return True

    def is_duplicate(self, exc: IntegrityError) -> bool:
        return self._config.driver_type.is_duplicate(exc)


def setup_database(
    config: DatabaseConfig,
):
    async def _setup_database(state: State):
        provider = DatabaseProvider(config)
        state.database_provider = provider
        await provider.health_check()

    return _setup_database


def get_database_provider(request: Request):
    return request.app.state.database_provider
