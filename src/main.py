import fastapi

from src.core import settings
from src.routes import router
from utils.events import create_event_handlers
from utils.providers.database import setup_database


def get_application() -> fastapi.FastAPI:
    settings.config.raise_on_error()
    application = fastapi.FastAPI()
    application.include_router(router)
    application.add_event_handler(
        'startup',
        create_event_handlers(
            application.state, setup_database(settings.database_config)
        ),
    )
    return application


app = get_application()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('src.main:app', host='127.0.0.1', port='8000')
