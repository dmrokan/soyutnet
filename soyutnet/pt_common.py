import sys
import asyncio
from weakref import ref, ReferenceType
from copy import deepcopy
from functools import reduce
from itertools import chain
import operator
from typing_extensions import (
    Any,
    AsyncGenerator,
    Dict,
    Tuple,
    Generator,
    Awaitable,
    Callable,
    TYPE_CHECKING,
    Self,
    Sequence,
    Set,
)

from .constants import *
from .token import Token
from .observer import Observer
from .validate import validate_net


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
        labels: Sequence[label_t] = (GENERIC_LABEL,),
    ) -> None:
        """
        Constructor.

        :param start: Place or transition. Input place of a transition (`end`), or input transition of a place (`end`).
        :param end: Place or transition. Output place of a transition (`start`), or output transition of a place (`start`).
        :param weight: Arc weight.
        :param labels: List of arc label.
        """
        self._start: ReferenceType[Any] | None = None
        """Input place/transition"""
        self.index_at_start: int = -1
        """Index in the list of output arcs of :py:attr:`soyutnet.pt_common.Arc.start`"""
        self._end: ReferenceType[Any] | None = None
        """Output place/transition"""
        self.index_at_end: int = -1
        """Index in the list of output arcs of :py:attr:`soyutnet.pt_common.Arc.end`"""
        self.weight: int = weight
        """Arc weight"""
        self._labels: tuple[label_t, ...] = tuple(labels)
        """The list of arc labels"""
        self._last_processed_label_index: int = 0
        self._queue: Queue = Queue(maxsize=weight)
        """Input/output queue for transmitting tokens from :py:attr:`soyutnet.pt_common.Arc.start` to :py:attr:`soyutnet.pt_common.Arc.end`"""

        self.start = start
        self.end = end

    @staticmethod
    def _validate(func: Any) -> Any:  # TODO: Fix annotation
        """
        Decorator to automatically validate a value provided to
        a setter is correct.
        """

        def wrapped(this: Self, *args: Any, **kwargs: Any) -> Any:
            output: Any = func(this, *args, **kwargs)
            validate_net(this, func, output, *args, **kwargs)
            return output

        return wrapped

    @property
    def start(self) -> Any:
        if self._start is not None:
            return self._start()

        return None

    @start.setter
    @_validate
    def start(self, s: Any) -> None:
        if s is not None:
            self._start = ref(s)
        else:
            self._start = s

    @property
    def end(self) -> Any:
        if self._end is not None:
            return self._end()

        return None

    @end.setter
    @_validate
    def end(self, e: Any) -> None:
        if e is not None:
            self._end = ref(e)
        else:
            self._end = e

    def __str__(self) -> str:
        """
        Returns the string representation of the arc.

        :return: String representation of the arc.
        """
        start_ident: str = ""
        start_ref: Any = self.start
        if start_ref is not None:
            start_ident = start_ref.ident()
        end_ident: str = ""
        end_ref: Any = self.end
        if end_ref is not None:
            end_ident = end_ref.ident()
        return (
            f"{start_ident}:{self.index_at_start} -> {end_ident}:{self.index_at_end}, "
            f"l={{{self._labels}}}, w={self.weight}"
        )

    @_validate
    def __rshift__(self, pt: Any) -> Any:
        return self.start.__rshift__(pt, self)

    @_validate
    def __lshift__(self, pt: Any) -> Any:
        return self.start.__lshift__(pt, self)

    @_validate
    def __gt__(self, pt: Any) -> Any:
        return self.start.__gt__(pt, self)

    @_validate
    def __lt__(self, pt: Any) -> Any:
        return self.start.__lt__(pt, self)

    async def wait(self) -> AsyncGenerator[TokenType, None]:
        """
        Acquires :py:attr:`soyutnet.pt_common.Arc.weight` tokens \
        from :py:attr:`soyutnet.pt_common.Arc.start` and yields them \
        to :py:attr:`soyutnet.pt_common.Arc.end`

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
        It is checked by the output transition at :py:attr:`soyutnet.pt_common.Arc.end` \
        to detemine the transition is enabled or not.

        :return: ``True`` if enabled.
        """
        return self._queue.full()

    async def observe_input_places(self, requester: str = "") -> None:
        """
        It is called by the output transition at :py:attr:`soyutnet.pt_common.Arc.end` \
        after the transition is enabled.

        It records the tokens counts just before the transition happens.

        :param requester: The identity of caller.
        """
        start_ref: Any = self.start
        if start_ref is not None:
            await start_ref.observe(requester=requester)

    async def notify_observer(self, label: label_t, increment: int = -1) -> None:
        """
        Called from :meth:`soyutnet.transition.Transition._process_input_arcs`
        when the transition is fired.
        """
        start_ref: Any = self.start
        if start_ref is not None and start_ref._observer is not None:
            await start_ref._observer.inc_token_count(label, increment)

    def get_graphviz_definition(
        self, t: int = 0, label_names: Dict[int, str] = {}
    ) -> str:
        """
        Generates graphviv DOT formated edge definition for the arc.

        :param t: Event index for clustering multiple steps of PT net simulation.
        :return: Edge definition.
        """
        start_ref: Any = self.start
        end_ref: Any = self.end
        if end_ref is not None and start_ref is not None:
            labels_: list[str] = []
            for l in self._labels:
                if (
                    l == GENERIC_LABEL
                    and l not in label_names
                    and len(self._labels) == 1
                ):
                    continue
                labels_.append(str(l) if l not in label_names else label_names[l])
            label_str: str = (
                "{" + ",".join([str(l) for l in labels_]) + "}" if labels_ else ""
            )
            arc_label: str = (
                str(self.weight) + " " if self.weight > 1 else ""
            ) + label_str
            return f"""{start_ref._name}_{t} -> {end_ref._name}_{t} [fontsize="20",label="{arc_label.strip()}",minlen="2",penwidth="3"];"""

        return ""

    def labels(
        self, remember_last_processed: bool = False
    ) -> Generator[label_t, None, None]:
        """
        Generator to iterate through arc labels, :attr:`._labels`.

        :param remember_last_processed: Continue iteration from the last index \
                                        recorded a previous iteration.
        """
        count: int = len(self._labels)
        i: int = 0
        while i < count:
            j: int = self._last_processed_label_index if remember_last_processed else i
            i += 1
            if remember_last_processed:
                self._last_processed_label_index += 1
                if self._last_processed_label_index >= count:
                    self._last_processed_label_index = 0
            yield self._labels[j]


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
        :param initial_tokens: Dictionary of initial tokens, in other words initial \
                               marking of the place.
        :param processor: Custom token processing function that is called between \
                          processing input and output arcs.
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
        self._tokens: TokenWalletType = deepcopy(initial_tokens)
        """Keeps tokens"""
        self._observer: Observer | None = None
        """Observes the tokens before each firing of output transitions"""
        self._processor: Callable[["PTCommon"], Awaitable[bool]] | None = processor
        """Custom token processing function that is called between processing input and output arcs"""

    def __rshift__(
        self, pt_arc: Self | Arc | Set[Self], arc: Arc | None = None
    ) -> Self | Arc:
        """
        Used for readable connection syntax

        e.g. ``p1 >> t >> p2``

        * ``pt_arc`` is a ``PTCommon`` instance:
            ``pt1 >> pt2``, calls ``pt1.connect(pt2)`` and returns ``pt2``.
        * ``pt_arc`` is an ``Arc`` instance:
            ``pt >> arc``, sets ``arc.start = self`` and returns ``arc``.
        * ``pt_arc`` is a ``set``: Runs,

            .. code:: python

               out = self
               for entry in pt_arc:
                   out = out >> entry
               assert out == entry

            and, returns ``out``.

        Examples: :doc:`/connection_examples`

        :param pt_arc: PTCommon instance, Arc or set of PTCommon instances
        :param arc: Provides weight and labels of the arc when ``pt_arc`` is a ``PTCommon`` instance.
        :return: pt_arc if pt_arc is a PTCommon or Arc instance, \
                 last entry of the set if pt_arc is a set.
        """
        if isinstance(pt_arc, Arc):
            pt_arc.start = self
            return pt_arc
        elif isinstance(pt_arc, set):
            rshift = lambda value, entry: value.__rshift__(entry, arc=arc)
            return reduce(rshift, pt_arc, self)
        else:
            weight: int = 1
            labels: Sequence[label_t] = []
            if arc is not None:
                weight = arc.weight
                labels = arc._labels
            return self.connect(pt_arc, weight=weight, labels=labels)

    def __gt__(
        self, pt_arc: Self | Arc | Set[Self], arc: Arc | None = None
    ) -> Self | Arc:
        """
        Used for readable connection syntax

        e.g. ``p1 > t > p2``

        * ``pt_arc`` is a ``PTCommon`` instance:
            ``pt1 > pt2``, calls ``pt1.connect(pt2)`` and returns ``pt1``.
        * ``pt_arc`` is an ``Arc`` instance:
            ``pt > arc``, sets ``arc.start = self`` and returns ``arc``.
        * ``pt_arc`` is a ``set``: Runs,

          .. code:: python

             out = self
             for entry in pt_arc:
                 out = out > entry
             assert out == self

          and, returns ``out``.

        Examples: :doc:`/connection_examples`

        :param pt_arc: PTCommon instance, Arc or set of PTCommon instances
        :return: self if pt_arc is a PTCommon or Arc instance, \
                 self if pt_arc is a set.
        """
        if isinstance(pt_arc, Arc):
            return self.__rshift__(pt_arc, arc)
        elif isinstance(pt_arc, set):
            gt = lambda value, entry: value.__gt__(entry, arc=arc)
            return reduce(gt, pt_arc, self)
        else:
            self.__rshift__(pt_arc, arc)
            return self

    def __lshift__(
        self, pt_arc: Self | Arc | Set[Self], arc: Arc | None = None
    ) -> Self | Arc:
        """
        Used for readable connection syntax

        e.g. ``p1 << t << p2``

        * ``pt_arc`` is a ``PTCommon`` instance:
            ``pt1 << pt2``, calls ``pt2.connect(pt1)`` and returns ``pt2``.
        * ``pt_arc`` is an ``Arc`` instance:
            ``pt << arc``, sets ``arc.start = self`` and returns ``arc``.
        * ``pt_arc`` is a ``set``: Runs,

            .. code:: python

               out = self
               for entry in pt_arc:
                   out = out << entry
               assert out == entry

            and, returns ``out``.

        Examples: :doc:`/connection_examples`

        :param pt_arc: PTCommon instance, Arc or set of PTCommon instances
        :return: pt_arc if pt_arc is a PTCommon or Arc instance, \
                 last entry of the set if pt_arc is a set.
        """
        if isinstance(pt_arc, Arc):
            return self.__rshift__(pt_arc, arc)
        elif isinstance(pt_arc, set):
            lshift = lambda value, entry: value.__lshift__(entry, arc=arc)
            return reduce(lshift, pt_arc, self)
        else:
            pt_arc.__rshift__(self, arc)
            return pt_arc

    def __lt__(
        self, pt_arc: Self | Arc | Set[Self], arc: Arc | None = None
    ) -> Self | Arc:
        """
        Used for readable connection syntax

        e.g. ``p1 < t < p2``

        * ``pt_arc`` is a ``PTCommon`` instance:
            ``pt1 < pt2``, calls ``pt1.connect(pt2)`` and returns ``pt1``.
        * ``pt_arc`` is an ``Arc`` instance:
            ``pt < arc``, sets ``arc.start = self`` and returns ``arc``.
        * ``pt_arc`` is a ``set``: Runs,

            .. code:: python

               out = self
               for entry in pt_arc:
                   out = out < entry
               assert out == self

            and, returns ``out``.

        Examples: :doc:`/connection_examples`

        :param pt_arc: PTCommon instance, Arc or set of PTCommon instances
        :return: self if pt_arc is a PTCommon or Arc instance, \
                 self if pt_arc is a set.
        """
        if isinstance(pt_arc, Arc):
            return self.__rshift__(pt_arc, arc)
        if isinstance(pt_arc, set):
            lt = lambda value, entry: value.__lt__(entry, arc=arc)
            return reduce(lt, pt_arc, self)
        else:
            self.__lshift__(pt_arc, arc)
            return self

    def _put_token(self, token: TokenType, strict: bool = True) -> int:
        """
        Places tokens into a list based on its label.

        :param token: A label and ID pair.
        :param strict: If set the label of token must already be \
                       in :py:attr:`soyutnet.pt_common.PTCommon._tokens` dictionary.
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
                self.net.ERROR_V(
                    f"{e} [{exc_tb.tb_frame}, {exc_tb.tb_lineno}, {exc_tb.tb_lasti}]"
                )
        except IndexError as e:
            """Raised when no token left with ``label`` in ``self._tokens``."""
            # TODO: Is it a model error or can be passed?
            _, _, exc_tb = sys.exc_info()
            if exc_tb is not None:
                self.net.ERROR_V(
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
            j: int = self._last_processed_input_arc_index
            self._last_processed_input_arc_index += 1
            if self._last_processed_input_arc_index == count:
                self._last_processed_input_arc_index = 0
            i += 1
            yield self._input_arcs[j]

    async def _get_output_arcs(self) -> AsyncGenerator[Arc, None]:
        """
        Generator to iterate through output arcs.

        :return: Output arcs.
        """
        count: int = len(self._output_arcs)
        i: int = 0
        while i < count:
            j: int = self._last_processed_output_arc_index
            self._last_processed_output_arc_index += 1
            if self._last_processed_output_arc_index == count:
                self._last_processed_output_arc_index = 0
            i += 1
            yield self._output_arcs[j]

    async def _process_input_arcs(self) -> bool:
        """
        Acquires tokens from enabled input arcs and stores them.

        :return: If ``True`` proceeds to processing tokens and output arcs, else continues waiting for enabled arcs.
        """
        self.net.DEBUG_V(f"{self.ident()}: process_input_arcs")
        async for arc in self._get_input_arcs():
            if not arc.is_enabled():
                self.net.DEBUG_V(f"Not enabled {arc}")
                continue
            async for token in arc.wait():
                self.net.DEBUG_V(f"Received '{token}' from {arc}")
                self._put_token(token)
                if self._observer is not None:
                    await self._observer.inc_token_count(token[0])

        return True

    async def _process_output_arcs(self) -> None:
        """
        Sends tokens to the output PTs.
        """
        self.net.DEBUG_V(f"{self.ident()}: process_output_arcs")
        async for arc in self._get_output_arcs():
            if arc.is_enabled():
                continue
            token: TokenType = tuple()
            for label in arc.labels(remember_last_processed=True):
                token = self._get_token(label)
                if token:
                    break
            if not token:
                self.net.DEBUG_V(f"No token, skipping '{arc}'")
                continue
            self.net.DEBUG_V(f"Sending '{token}' to {arc}")
            await arc.send(token)

    async def _process_tokens(self) -> bool:
        """
        Processes input tokens before sending if required.

        :return: ``True`` by default, else goes back to :py:func:`soyutnet.pt_common.PTCommon._process_input_arcs`.
        """
        self.net.DEBUG_V(f"{self.ident()}: process_tokens")
        if self._processor is None:
            return True

        return await self._processor(self)

    async def _observe(self, requester: str = "") -> None:
        """
        Dummy observer.
        """
        pass

    async def _set_initial_marking(self) -> None:
        if self._observer is not None:
            for label in self._tokens:
                await self._observer.inc_token_count(
                    label, self._get_token_count(label)
                )

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
        self, other: Self, weight: int = 1, labels: Sequence[label_t] = [GENERIC_LABEL]
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
        for label in arc.labels():
            if label not in self._tokens:
                self._tokens[label] = []
            if label not in other._tokens:
                other._tokens[label] = []
        self.net.DEBUG_V(f"{self.ident()}: Connected arc: {str(arc)}")

        return other

    async def observe(self, requester: str = "") -> None:
        """
        Public observe function called by output arcs.

        :param requester: The identity of caller.
        """
        await self._observe(requester=requester)

    def put_token(self, label: label_t = GENERIC_LABEL, id: id_t = GENERIC_ID) -> int:
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

    def get_sorted_input_arcs(self) -> list[Arc]:
        return sorted(self._input_arcs, key=lambda arc: arc.start._name)

    def is_dangling(self) -> bool:
        for arc in chain(self._input_arcs, self._output_arcs):
            match arc.start, arc.end:
                case PTCommon(), PTCommon():
                    return False

        return True


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

    await pt._set_initial_marking()
    pt.net.DEBUG_V(f"{pt.ident()}: Loop started")

    while await pt.should_continue():
        await pt.net.sleep(pt.net.LOOP_DELAY)

    pt.net.DEBUG_V(f"{pt.ident()}: Loop ended")
