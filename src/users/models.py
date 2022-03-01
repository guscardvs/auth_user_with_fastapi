from datetime import date, datetime
from uuid import UUID

from pydantic.networks import EmailStr

from utils.model import Model, get_optional_model


class User(Model):
    id_: int
    external_id: UUID
    name: str
    email: str
    password: str
    birth_date: date
    date_joined: datetime


class CreateUser(Model):
    name: str
    email: EmailStr
    password: str
    birth_date: date


EditUser = get_optional_model(CreateUser)


class ReadUser(Model):
    external_id: UUID
    name: str
    email: str
    birth_date: date
