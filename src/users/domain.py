from src.users import models, repository
from utils import timezone
from utils.providers import database, external_id, password


def enclose(payload: models.User) -> models.ReadUser:
    return models.ReadUser.parse_obj(payload)


class CreateUserUseCase:
    def __init__(
        self,
        database_provider: database.DatabaseProvider,
        payload: models.CreateUser,
    ) -> None:
        self._database_provider = database_provider
        self._payload = self._prepare_payload(payload)

    def _prepare_payload(self, payload: models.CreateUser):
        return models.CreateUser(
            name=payload.name,
            email=payload.email,
            password=password.hash(payload.password),
            birth_date=payload.birth_date,
        )

    async def execute(self):
        ext_id = external_id.generate()
        date_joined = timezone.now()
        result = await repository.UserRepository(
            self._database_provider
        ).create(ext_id, date_joined, self._payload)
        return enclose(result)


class RetrieveUserByEmailUseCase:
    def __init__(
        self,
        database_provider: database.DatabaseProvider,
        email: str,
    ) -> None:
        self._database_provider = database_provider
        self._email = email

    async def execute(self):
        result = await repository.UserRepository(
            self._database_provider
        ).retrieve('email', self._email)
        return enclose(result)


class EditUserByEmailUseCase:
    def __init__(
        self,
        database_provider: database.DatabaseProvider,
        email: str,
        payload: models.EditUser,
    ) -> None:
        self._database_provider = database_provider
        self._email = email
        self._payload = payload

    async def execute(self):
        result = await repository.UserRepository(self._database_provider).edit(
            self._email, self._payload
        )
        return enclose(result)
