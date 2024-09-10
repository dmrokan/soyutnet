import asyncio
import signal
import functools
from typing import Any

from .pt_common import PTRegistry, PTCommon


def _int_handler(
    signame: str, loop: asyncio.AbstractEventLoop, pt_registry: PTRegistry
) -> None:
    print(f"Got signal '{signame}'")

    if signame == "SIGINT" or signame == "SIGTERM":
        print(">>>>>>>>>>>>>>>>>>>>>>>>> <<<<<<<<<<<<<<<<<<<<<<<<<")
        loop.stop()


def _add_int_handlers(pt_registry: PTRegistry) -> None:
    loop = asyncio.get_running_loop()

    for signame in {"SIGINT", "SIGTERM"}:
        loop.add_signal_handler(
            getattr(signal, signame),
            functools.partial(_int_handler, signame, loop, pt_registry),
        )


def _cancel_all_tasks() -> None:
    tasks: set[asyncio.Task[Any]] = asyncio.all_tasks()
    for task in tasks:
        task.cancel()


def terminate() -> None:
    """
    Terminates PT net simulation.
    """
    _cancel_all_tasks()


async def main(pt_registry: PTRegistry, debug_level: str = "ERROR") -> None:
    """
    Main entry point of PT net simulation.

    Runs the tasks assigned to places and transitions registered in ``pt_registry``.

    :param pt_registry: Registry object keeping all places and transitions in the model.
    :param debug_level: Set debug level to ``"ERROR", "DEBUG"`` or ``"INFO"``.
    """
    from . import global_defs

    if debug_level == "INFO":
        global_defs.VERBOSE_ENABLED = True
        debug_level = "DEBUG"
    if debug_level == "DEBUG":
        global_defs.DEBUG_ENABLED = True

    tasks: set[asyncio.Task[PTCommon]] = set()

    _add_int_handlers(pt_registry)
    for loop in pt_registry.get_loops():
        task: asyncio.Task[Any] = asyncio.create_task(loop)
        tasks.add(task)
        task.add_done_callback(tasks.discard)

    await asyncio.gather(*tasks, return_exceptions=False)
