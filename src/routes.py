import fastapi

from src.users.routes import router as user_router
from utils.providers import database

router = fastapi.APIRouter()

router.include_router(user_router, prefix='/users', tags=['Users'])


@router.get('/health-check')
async def healthcheck(
    database_provider: database.DatabaseProvider = fastapi.Depends(
        database.get_database_provider
    ),
):
    return {'status': True, 'database': await database_provider.health_check()}
