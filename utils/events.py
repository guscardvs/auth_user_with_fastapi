import asyncio
from typing import Awaitable, Callable

from starlette.datastructures import State


def create_event_handlers(
    state: State, *handlers: Callable[[State], Awaitable[None]]
):
    async def handler():
        await asyncio.gather(*(handler(state) for handler in handlers))

    return handler
