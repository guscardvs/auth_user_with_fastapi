import fastapi
from pydantic.networks import EmailStr

from src.users import domain, models
from utils.providers import database

router = fastapi.APIRouter()


@router.get('/{email}', response_model=models.ReadUser)
async def get_user(
    email: EmailStr = fastapi.Path(...),
    database_provider: database.DatabaseProvider = fastapi.Depends(
        database.get_database_provider
    ),
):
    return await domain.RetrieveUserByEmailUseCase(
        database_provider, email
    ).execute()


@router.post('/', response_model=models.ReadUser)
async def create_user(
    payload: models.CreateUser = fastapi.Body(...),
    database_provider: database.DatabaseProvider = fastapi.Depends(
        database.get_database_provider
    ),
):
    return await domain.CreateUserUseCase(database_provider, payload).execute()


@router.patch('/{email}', response_model=models.ReadUser)
async def update_user(
    email: EmailStr = fastapi.Path(...),
    payload: models.EditUser = fastapi.Body(...),
    database_provider: database.DatabaseProvider = fastapi.Depends(
        database.get_database_provider
    ),
):
    return await domain.EditUserByEmailUseCase(
        database_provider, email, payload
    ).execute()
