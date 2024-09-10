import asyncio
from typing import Any

from .global_defs import *


INVALID_LABEL = -10
INVALID_ID = -11
GENERIC_LABEL = 0
"""Generic label"""
GENERIC_ID = 0
"""Generic ID"""
INITIAL_ID = 0


class SoyutNetError(Exception):
    def __init__(self, message: str = "An error occured.") -> None:
        self.message: str = message
        super().__init__(self.message)


async def sleep(amount: float = 0.0) -> None:
    await asyncio.sleep(amount)


def time() -> float:
    loop = asyncio.get_running_loop()
    return loop.time()


def get_loop_name() -> str:
    name: str = "NO-LOOP"
    try:
        task: asyncio.Task[Any] | None = asyncio.current_task()
        if isinstance(task, asyncio.Task):
            name = task.get_name()
    except RuntimeError:
        pass

    return name


def _DEBUG(*args: Any) -> None:
    pass


def _DEBUG_V(*args: Any) -> None:
    print(f"{get_loop_name()}:", *args)


def ERROR_V(*args: Any) -> None:
    _DEBUG_V("ERR:", *args)


def _DEBUG_NOP(*args: Any) -> None:
    pass


if DEBUG_ENABLED:
    DEBUG = _DEBUG_V
    VERBOSE_DEBUG_ENABLED = VERBOSE_ENABLED
else:
    DEBUG = _DEBUG_NOP
    VERBOSE_DEBUG_ENABLED = False

if VERBOSE_DEBUG_ENABLED:
    DEBUG_V = _DEBUG_V
else:
    DEBUG_V = _DEBUG_NOP

if not VERBOSE_ENABLED:
    ERROR_V = _DEBUG_NOP
