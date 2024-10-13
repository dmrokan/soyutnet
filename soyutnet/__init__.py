import sys
import os
import asyncio
import signal
import functools
from typing import Any, Type, Coroutine, TextIO
import logging

from .constants import *
from .registry import PTRegistry, TokenRegistry
from .pt_common import PTCommon, Arc
from .observer import MergedRecordsType, Observer, ComparativeObserver
from .transition import Transition
from .place import Place, SpecialPlace
from .token import Token


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


async def main(
    pt_registry: PTRegistry, extra_routines: list[Coroutine[Any, Any, None]] = []
) -> None:
    """
    Main entry point of PT net simulation.

    Runs the tasks assigned to places and transitions registered in ``pt_registry``.

    :param pt_registry: Registry object keeping all places and transitions in the model.
    :param extra_routines: Asyncio task functions to be run additional to the PT net loops.
    """
    tasks: set[asyncio.Task[PTCommon]] = set()

    _add_int_handlers(pt_registry)
    for loop in pt_registry.get_loops():
        task: asyncio.Task[Any] = asyncio.create_task(loop)
        tasks.add(task)
        task.add_done_callback(tasks.discard)

    for r in extra_routines:
        task = asyncio.create_task(r)
        tasks.add(task)
        task.add_done_callback(tasks.discard)

    await asyncio.gather(*tasks, return_exceptions=False)


def run(*args: Any, ignore_cancelled_exception: bool = True, **kwargs: Any) -> None:
    try:
        asyncio.run(main(*args, **kwargs))
    except asyncio.exceptions.CancelledError as e:
        if not ignore_cancelled_exception:
            raise asyncio.exceptions.CancelledError(e)


class SoyutNet(object):
    def __init__(self) -> None:
        self._LOOP_DELAY: float = 0.5
        self.DEBUG_ENABLED: bool = False
        """if set, :py:func:`soyutnet.SoyutNet.DEBUG` will print."""
        self._VERBOSE_ENABLED: bool = False
        """if set, :py:func:`soyutnet.SoyutNet.DEBUG_V` will print."""
        self.SLOW_MOTION: bool = False
        """If set, task loops are delayed for :py:attr:`soyutnet.SoyutNet.LOOP_DELAY` seconds"""
        self.FLOAT_DECIMAL_PLACE_FORMAT: int = 6
        """Number of decimal places of floats in debug prints"""
        self._LOG_FILE: str = ""
        """Name of the log file"""
        self._logger: logging.Logger | None = None
        """Log handler"""

    @property
    def LOG_FILE(self) -> str:
        return self._LOG_FILE

    @LOG_FILE.setter
    def LOG_FILE(self, filename: str | None) -> None:
        if filename is not None:
            self._LOG_FILE = filename
            self._logger = logging.getLogger(self.__class__.__name__)
            self._logger.addHandler(logging.FileHandler(filename))
        else:
            self._logger = None

    @property
    def VERBOSE_ENABLED(self) -> bool:
        return self._VERBOSE_ENABLED

    @VERBOSE_ENABLED.setter
    def VERBOSE_ENABLED(self, enabled: bool) -> None:
        self._VERBOSE_ENABLED = enabled
        logging.basicConfig(level=logging.INFO)

    def __sprint(self, *args: Any, depth: int = 0, separator: str = " ") -> str:
        output = ""
        for a in args:
            match a:
                case tuple():
                    output += (
                        "(" + self.__sprint(*a, depth=depth + 1, separator=", ") + ")"
                    )
                case list():
                    output += (
                        "["
                        + self.__sprint(*a, depth=depth + 1, separator=", ")
                        + "]"
                        + os.linesep
                    )
                case float():
                    output += f"{a:.{self.FLOAT_DECIMAL_PLACE_FORMAT}f}"
                case _:
                    output += str(a)
            output += separator

        if depth == 0:
            output += os.linesep

        return output

    def __print(self, *args: Any, file: TextIO = sys.stdout, **kwargs: Any) -> None:
        file.write(self.__sprint(*args, **kwargs))

    def _print(self, *args: Any, file: TextIO = sys.stdout, **kwargs: Any) -> None:
        if self._logger is not None:
            self._logger.info(self.__sprint(*args, depth=1, **kwargs))
        else:
            self.__print(*args, file=file, **kwargs)

    def _error(self, *args: Any, file: TextIO = sys.stdout, **kwargs: Any) -> None:
        if self._logger is not None:
            self._logger.error(self.__sprint(*args, depth=1, **kwargs))
        else:
            self.__print("ERR:", file=file, depth=1, **kwargs)
            self._print(*args, **kwargs)

    @property
    def LOOP_DELAY(self) -> float:
        """
        Asyncio tasks main loop delay for debugging.

        :return: Delay amount in seconds.
        """
        if self.SLOW_MOTION:
            return self._LOOP_DELAY
        return 0

    @LOOP_DELAY.setter
    def LOOP_DELAY(self, amount: float) -> None:
        self._LOOP_DELAY = amount

    async def sleep(self, amount: float = 0.0) -> None:
        """
        Wrapper for task sleep function.

        :param amount: Sleep amount in seconds.
        """
        await asyncio.sleep(amount)

    def time(self) -> float:
        """
        Get current time since the program starts.

        :return: Current time in seconds.
        """
        loop = asyncio.get_running_loop()
        return loop.time()

    def get_loop_name(self) -> str:
        """
        Get the name of current loop which this function is called from.

        :return: Name of the loop.
        """
        name: str = "NO-LOOP"
        try:
            task: asyncio.Task[Any] | None = asyncio.current_task()
            if isinstance(task, asyncio.Task):
                name = task.get_name()
        except RuntimeError:
            pass

        return name

    def DEBUG_V(self, *args: Any) -> None:
        """
        Print debug messages when :py:attr:`soyutnet.SoyutNet.VERBOSE_ENABLED`.
        """
        if self.DEBUG_ENABLED and self._VERBOSE_ENABLED:
            self._error(f"{self.get_loop_name()}:", *args)

    def ERROR_V(self, *args: Any) -> None:
        """
        Print error messages when :py:attr:`soyutnet.SoyutNet.VERBOSE_ENABLED`.
        """
        if self._VERBOSE_ENABLED:
            self._error(f"{self.get_loop_name()}:", *args, file=sys.stderr)

    def DEBUG(self, *args: Any) -> None:
        """
        Print debug messages when :py:attr:`soyutnet.SoyutNet.DEBUG_ENABLED`.
        """
        if self.DEBUG_ENABLED:
            self._print(f"{self.get_loop_name()}:", *args)

    def ERROR(self, *args: Any) -> None:
        """
        Print error messages.
        """
        self._error(f"{self.get_loop_name()}:", *args, file=sys.stderr)

    def Token(self, *args: Any, **kwargs: Any) -> Token:
        kwargs["net"] = self
        return Token(*args, **kwargs)

    def Place(self, *args: Any, **kwargs: Any) -> Place:
        kwargs["net"] = self
        return Place(*args, **kwargs)

    def SpecialPlace(self, *args: Any, **kwargs: Any) -> SpecialPlace:
        kwargs["net"] = self
        return SpecialPlace(*args, **kwargs)

    def Transition(self, *args: Any, **kwargs: Any) -> Transition:
        kwargs["net"] = self
        return Transition(*args, **kwargs)

    def Observer(self, *args: Any, **kwargs: Any) -> Observer:
        kwargs["net"] = self
        return Observer(*args, **kwargs)

    def ComparativeObserver(self, *args: Any, **kwargs: Any) -> ComparativeObserver:
        kwargs["net"] = self
        return ComparativeObserver(*args, **kwargs)

    def TokenRegistry(self, *args: Any, **kwargs: Any) -> TokenRegistry:
        kwargs["net"] = self
        return TokenRegistry(*args, **kwargs)

    def PTRegistry(self, *args: Any, **kwargs: Any) -> PTRegistry:
        kwargs["net"] = self
        return PTRegistry(*args, **kwargs)

    def print(self, *args: Any, **kwargs: Any) -> None:
        self._print(*args, **kwargs)
