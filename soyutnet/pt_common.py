import sys
import asyncio
from typing import (
    Any,
    AsyncGenerator,
    Self,
    Dict,
    Tuple,
    Coroutine,
    Generator,
    Awaitable,
    Callable,
    TYPE_CHECKING,
)

from .global_defs import *
from . import common as _c
from .registry import Registry
from .token import Token
from .observer import Observer
from weakref import ref, ReferenceType


if TYPE_CHECKING:
    Queue = asyncio.Queue[Any]
else:
    Queue = asyncio.Queue


class Arc(object):
    """
    Defines a generic labeled PT net arc which connects places to transitions or vice versa.
    """

    def __init__(
        self,
        start: Any,
        end: Any,
        weight: int = 1,
        labels: list[label_t] = [_c.GENERIC_LABEL],
    ) -> None:
        """
        Constructor.

        :param start: Place or transition. Input place of a transition (`end`), or input transition of a place (`end`).
        :param end: Place or transition. Output place of a transition (`start`), or output transition of a place (`start`).
        :param weight: Arc weight.
        :param labels: List of arc label.
        """
        self.start: ReferenceType[Any] = ref(start)
        """Input place/transition"""
        self.index_at_start: int = -1
        """Index in the list of output arcs of :py:attr:`self.start`"""
        self.end: ReferenceType[Any] = ref(end)
        """Output place/transition"""
        self.index_at_end: int = -1
        """Index in the list of input arcs of :py:attr:`self.end`"""
        self.weight: int = weight
        """Arc weight"""
        self.labels: list[label_t] = list(labels)
        """The list of arc labels"""
        self._queue: Queue = Queue(maxsize=weight)
        """Input/output queue for transmitting tokens from :py:attr:`self.start` to :py:attr:`self.end`"""

    def __str__(self) -> str:
        """
        Returns string representation of the arc.

        :return: String representation of the arc.
        """
        start_ident: str = ""
        start_ref: Any = self.start()
        if start_ref is not None:
            start_ident = start_ref.ident()
        end_ident: str = ""
        end_ref: Any = self.end()
        if end_ref is not None:
            end_ident = end_ref.ident()
        return (
            f"{start_ident}:{self.index_at_start} -> {end_ident}:{self.index_at_end}, "
            f"l={self.labels}, w={self.weight}"
        )

    async def wait(self) -> AsyncGenerator[TokenType, None]:
        """
        Acquires :py:attr:`self.weight` tokens from :py:attr:`self.start` and yields them to :py:attr:`self.end`

        :return: Tokens.
        """
        count: int = self.weight
        while count > 0:
            token: TokenType = await self._queue.get()
            self._queue.task_done()
            count -= 1
            yield token

    async def send(self, token: TokenType) -> None:
        """
        Puts a token to the output arc.

        :param token: Token.
        """
        if not token:
            return
        await self._queue.put(token)

    def is_enabled(self) -> bool:
        """
        It is checked by the output transition at :py:attr:`self.end` to detemine the transition is enabled or not.

        :return: ``True`` if enabled.
        """
        return self._queue.full()

    async def observe_input_places(self) -> None:
        """
        It is called by the output transition at :py:attr:`self.end` after the transition is enabled.

        It records the tokens counts just before the transition happens.
        """
        start_ref: Any = self.start()
        if start_ref is not None:
            await start_ref.observe(self._queue.qsize())


class PTCommon(Token):
    """
    Base class implementing shared properties of places and transitions.
    """

    def __init__(
        self,
        name: str = "",
        initial_tokens: TokenWalletType = {},
        processor: Callable[["PTCommon"], Awaitable[bool]] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Constructor.

        :param name: Name of the place or transition.
        :param initial_tokens: Dictionary of initial tokens, in other words initial marking of the place.
        :param processor: Custom token processing function that is called between processing input and output arcs.
        """
        super().__init__(**kwargs)
        self._name: str = name
        """Name of the PT"""
        self._input_arcs: list[Arc] = []
        """List of input arcs"""
        self._last_processed_input_arc_index: int = 0
        self._output_arcs: list[Arc] = []
        """List of output arcs"""
        self._last_processed_output_arc_index: int = 0
        self._tokens: TokenWalletType = {
            label: list(initial_tokens[label]) for label in initial_tokens
        }
        """Keeps tokens"""
        self._observer: Observer | None = None
        """Observes the tokens before each firing of output transitions"""
        self._ident: str = self.ident()
        """Unique identifier"""
        self._processor: Callable[["PTCommon"], Awaitable[bool]] | None = processor
        """Custom token processing function that is called between processing input and output arcs"""

    def _put_token(self, token: TokenType, strict: bool = True) -> int:
        """
        Places tokens into a list based on its label.

        :param token: A label and ID pair.
        :param strict: If set the label of token must already be in :py:attr:`self._tokens` dictionary.
        :return: Number of tokens with the given label.
        """
        label: label_t = token[0]
        id: id_t = token[1]
        """NOTE: ``connect`` must add an item with key = ``label`` to the ``self._tokens`` dict."""
        if not strict and label not in self._tokens:
            self._tokens[label] = []
        try:
            self._tokens[label].append(id)
        except KeyError as e:
            # TODO: Handle model error
            _, _, exc_tb = sys.exc_info()
            if exc_tb is not None:
                raise RuntimeError(
                    f"{self.ident()}: {self._tokens} {label} {e} [{exc_tb.tb_frame}, {exc_tb.tb_lineno}, {exc_tb.tb_lasti}]"
                )
            raise KeyError(e)

        return self._get_token_count(label)

    def _get_token(self, label: label_t) -> TokenType:
        """
        Gets the first token with the given label from a FIFO list.

        :param label: Label.
        :return: Token.
        """
        try:
            id: id_t = self._tokens[label].pop(0)
            return (label, id)
        except KeyError as e:
            """Raised when label is not in ``self._tokens``."""
            # TODO: Handle model error
            _, _, exc_tb = sys.exc_info()
            if exc_tb is not None:
                _c.ERROR_V(
                    f"{e} [{exc_tb.tb_frame}, {exc_tb.tb_lineno}, {exc_tb.tb_lasti}]"
                )
        except IndexError as e:
            """Raised when no token left with ``label`` in ``self._tokens``."""
            # TODO: Is it a model error or can be passed?
            _, _, exc_tb = sys.exc_info()
            if exc_tb is not None:
                _c.ERROR_V(
                    f"{e} [{exc_tb.tb_frame}, {exc_tb.tb_lineno}, {exc_tb.tb_lasti}]"
                )

        return tuple()

    def _get_token_count(self, label: label_t) -> int:
        """
        Get the number of tokens with the given label.

        :param label: Label.
        :return: Number of tokens with the given label.
        """
        # TODO: Handle model error
        return len(self._tokens[label])

    async def _get_input_arcs(self) -> AsyncGenerator[Arc, None]:
        """
        Generator to iterate through input arcs.

        :return: Input arcs.
        """
        count: int = len(self._input_arcs)
        i: int = 0
        while i < count:
            yield self._input_arcs[self._last_processed_input_arc_index]
            self._last_processed_input_arc_index += 1
            if self._last_processed_input_arc_index == count:
                self._last_processed_input_arc_index = 0
            i += 1

    async def _get_output_arcs(self) -> AsyncGenerator[Arc, None]:
        """
        Generator to iterate through output arcs.

        :return: Output arcs.
        """
        count: int = len(self._output_arcs)
        i: int = 0
        while i < count:
            yield self._output_arcs[self._last_processed_output_arc_index]
            self._last_processed_output_arc_index += 1
            if self._last_processed_output_arc_index == count:
                self._last_processed_output_arc_index = 0
            i += 1

    async def _process_input_arcs(self) -> bool:
        """
        Acquires tokens from enabled input arcs and stores them.

        :return: If ``True`` proceeds to processing tokens and output arcs, else continues waiting for enabled arcs.
        """
        _c.DEBUG_V(f"{self._ident}: process_input_arcs")
        async for arc in self._get_input_arcs():
            if not arc.is_enabled():
                _c.DEBUG_V(f"Not enabled {arc}")
                continue
            async for token in arc.wait():
                _c.DEBUG_V(f"Received '{token}' from {arc}")
                self._put_token(token)
                if self._observer is not None:
                    await self._observer.inc_token_count(token[0])

        return True

    async def _process_output_arcs(self) -> None:
        """
        Sends tokens to the output PTs.
        """
        _c.DEBUG_V(f"{self._ident}: process_output_arcs")
        async for arc in self._get_output_arcs():
            token: TokenType = tuple()
            for label in arc.labels:
                token = self._get_token(label)
                if token:
                    break
            if not token:
                _c.DEBUG_V(f"No token, skipping '{arc}'")
                continue
            _c.DEBUG_V(f"Sending '{token}' to {arc}")
            await arc.send(token)
            if self._observer is not None:
                await self._observer.inc_token_count(token[0], inc=-1)

    async def _process_tokens(self) -> bool:
        """
        Processes input tokens before sending if required.

        :return: ``True`` by default, else goes back to :py:func:`self._process_input_arcs`.
        """
        _c.DEBUG_V(f"{self._ident}: process_tokens")
        if self._processor is None:
            return True

        return await self._processor(self)

    async def _observe(self, token_count_in_arc: int = 0) -> None:
        """
        Dummy observer.
        """
        pass

    def ident(self) -> str:
        """
        Returns the unique identifier of PT.

        :return: Unique identifier.
        """
        return f"({self._name}, {self._id})"

    async def should_continue(self) -> bool:
        """
        Main loop of async task assigned to the PT.

        :return: Continues task if `True`.
        """
        if not await self._process_input_arcs():
            return True

        if not await self._process_tokens():
            """If ``False`` do not process output arcs yet."""
            return True

        await self._process_output_arcs()

        return True

    def connect(
        self, other: Self, weight: int = 1, labels: list[label_t] = [_c.GENERIC_LABEL]
    ) -> Self:
        """
        Connects the output of `self` to the input of an other PT by creating an Arc in between.

        :param other: The place/transition which it will be connected to.
        :param weight: Arc weight.
        :param labels: List of arc labels.
        :return: Output place or transition that ``other`` references.
        """
        arc: Arc = Arc(start=self, end=other, weight=weight, labels=list(labels))
        self._output_arcs.append(arc)
        other._input_arcs.append(arc)
        arc.index_at_start = len(self._output_arcs) - 1
        arc.index_at_end = len(other._input_arcs) - 1
        for label in arc.labels:
            if label not in self._tokens:
                self._tokens[label] = []
            if label not in other._tokens:
                other._tokens[label] = []
        _c.DEBUG_V(f"{self._ident}: Connected arc: {str(arc)}")

        return other

    async def observe(self, token_count_in_arc: int = 0) -> None:
        """
        Public observe function called by output arcs.
        """
        await self._observe(token_count_in_arc)

    def put_token(
        self, label: label_t = _c.GENERIC_LABEL, id: id_t = _c.GENERIC_ID
    ) -> int:
        """
        Places tokens into a list based on its label.

        :param label: Label.
        :param id: ID.
        :return: Number of tokens with the given label.
        """
        return self._put_token((label, id))

    def get_token(self, label: label_t) -> TokenType:
        """
        Gets the first token with the given label from a FIFO list.

        :param label: Label.
        :return: A token if exists else empty token which is a null tuple (``tuple()``).
        """
        return self._get_token(label)

    def get_token_count(self, label: label_t) -> int:
        """
        Get the number of tokens with the given label.

        :param label: Label.
        :return: Number of tokens.
        """
        return self._get_token_count(label)


async def _loop(pt: PTCommon) -> None:
    """
    Task function assigned to the PT.

    :param pt: PTCommon instance.
    """
    task: asyncio.Task[Any] | None = asyncio.current_task()
    if isinstance(task, asyncio.Task):
        task.set_name(f"loop{pt.ident()}")
    else:
        return

    _c.DEBUG_V(f"{pt.ident()}: Loop started")

    while await pt.should_continue():
        await _c.sleep(LOOP_DELAY)
        pass

    _c.DEBUG_V(f"{pt.ident()}: Loop ended")


class PTRegistry(Registry):
    """
    Keeps track of PTCommon instances.
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        super().__init__()

    def get_loops(self) -> Generator[Coroutine[Any, Any, None], None, None]:
        """
        Yields asyncio task functions assigned to the PT.

        :return: Asyncio task function.
        """
        for label in self._directory:
            for entry in self._directory[label]:
                yield _loop(entry[1])

    def register(self, pt: PTCommon) -> id_t:  # type: ignore[override]
        """
        Registers a PT.

        :param pt: PTCommon instance.
        :return: Unique ID assigned to the PT.
        """

        def callback(new_id: id_t, pt: PTCommon) -> None:
            pt._id = new_id
            _c.DEBUG_V(f"Registered: {pt.ident()}")

        return super().register(pt, callback)
