import asyncio
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec('P')
CallableT = TypeVar('CallableT', bound=Callable)


def on_error(
    source: type[Exception],
    exc: Callable[P, Exception],
    *args: P.args,
    **kwargs: P.kwargs
):
    def outer(func: CallableT) -> CallableT:
        async def _async_inner(*f_args, **f_kwargs):
            try:
                response = await func(*f_args, **f_kwargs)
            except source as err:
                raise exc(*args, **kwargs) from err
            else:
                return response

        def _inner(*f_args, **f_kwargs):
            try:
                response = func(*f_args, **f_kwargs)
            except source as err:
                raise exc(*args, **kwargs) from err
            else:
                return response

        if asyncio.iscoroutinefunction(func):
            return wraps(func)(_async_inner)  # type: ignore
        return wraps(func)(_inner)  # type: ignore

    return outer
