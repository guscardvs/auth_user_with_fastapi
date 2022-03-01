import typing
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.users import models
from src.users.table import user_table
from utils import exc
from utils.helpers import on_error
from utils.providers.database import ConnectionContext, DatabaseProvider


class UserRepository:
    def __init__(self, database_provider: DatabaseProvider) -> None:
        self._provider = database_provider

    def serialize(self, obj: typing.Mapping[str, typing.Any]) -> models.User:
        return models.User.parse_obj(obj)

    @on_error(IntegrityError, exc.ConflictError, target='user')
    async def create(
        self,
        external_id: UUID,
        date_joined: datetime,
        payload: models.CreateUser,
    ):
        query = sa.insert(user_table).values(
            {
                'external_id': external_id,
                'date_joined': date_joined,
                **payload.dict(),
            }
        )
        async with self._provider.acquire() as conn:
            async with conn.begin():
                await conn.execute(query)
            result = await conn.execute(
                sa.select(user_table).where(
                    user_table.c.external_id == external_id
                )
            )
            return self.serialize(result.mappings().one())

    @on_error(NoResultFound, exc.NotFoundError, target='user')
    async def retrieve(self, field: str, value: typing.Any):
        context = self._provider.acquire()
        async with context:
            return await self._get(context, field, value)

    @on_error(NoResultFound, exc.NotFoundError, target='user')
    @on_error(IntegrityError, exc.ConflictError, target='user')
    async def edit(self, email: str, payload: models.EditUser):
        context = self._provider.acquire()
        update_query = (
            sa.update(user_table)
            .where(user_table.c.email == email)
            .values(payload.dict(exclude_none=True))
        )
        async with context as conn:
            await self._get(context, 'email', email)
            await conn.execute(update_query)
        return await self._get(context, 'email', payload.email or email)

    async def _get(
        self,
        connection_context: ConnectionContext,
        field: str,
        value: typing.Any,
    ):
        query = sa.select(user_table).where(
            getattr(user_table.c, field) == value
        )
        async with connection_context as conn:
            result = await conn.execute(query)
            return self.serialize(result.mappings().one())
