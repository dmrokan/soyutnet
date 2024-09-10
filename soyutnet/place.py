import asyncio
from typing import (
    Any,
    Tuple,
    Awaitable,
    Callable,
)

from .global_defs import *
from . import common as _c
from .pt_common import PTCommon, PTRegistry, Arc
from .observer import Observer


class Place(PTCommon):
    """
    Defines PTNet places.
    """

    def __init__(
        self,
        name: str = "",
        observer: Observer | None = None,
        observer_record_limit: int = 0,
        observer_verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Constructor

        :param name: Name of the place.
        :param observer: Observer instance assigned to the place.
        :param observer_record_limit: Maximum number of records that is recorded by the observer. It is unlimited when chosen ``0``.
        :param observer_verbose: If set, observer will print new records when saved.
        """
        super().__init__(name=name, **kwargs)
        self._observer: Observer = (
            Observer(observer_record_limit, verbose=observer_verbose)
            if observer is None
            else observer
        )
        if not self._observer._ident:
            self._observer._ident = self.ident()

    async def _observe(self, token_count_in_arc: int = 0) -> None:
        """
        Save token counts for each label to the observer's records.

        Also, add the number of tokens sent to the caller arc.

        :param token_count_in_arc: Number of tokens in the output arc of places must also be added to the count.
        """
        await self._observer.save(token_count_in_arc)


class SpecialPlace(Place):
    """
    Custom place class whose token processing methods can be overriden.
    """

    def __init__(
        self,
        name: str = "",
        consumer: Callable[["SpecialPlace"], Awaitable[bool]] | None = None,
        producer: Callable[["SpecialPlace"], Awaitable[TokenType]] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Constructor.

        :param name: Name of the place.
        :param consumer: Custom :py:func:`place._process_input_arcs` function.
        :param producer: Custom :py:func:`place._process_output_arcs` function.
        """
        super().__init__(name=name, **kwargs)
        self._consumer: Callable[["SpecialPlace"], Awaitable[bool]] | None = consumer
        """Custom :py:func:`place._process_input_arcs` function."""
        self._producer: Callable[["SpecialPlace"], Awaitable[TokenType]] | None = (
            producer
        )
        """Custom :py:func:`place._process_output_arcs` function."""

    async def _process_input_arcs(self) -> bool:
        """
        Calls custom producer function. If it is ``None`` calls :py:func:`place._process_input_arcs` function.

        :return: If ``True`` continues to processing tokens and output arc, else loops back to processing input arcs.
        """
        if self._producer is not None:
            token: TokenType = await self._producer(self)
            if not token:
                return False

            label: label_t = token[0]
            count: int = self._put_token(token, strict=False)
            if self._observer is not None:
                await self._observer.inc_token_count(token[0])

            return True
        else:
            return await super()._process_input_arcs()

    async def _process_output_arcs(self) -> None:
        """
        Null process output arcs function, when a custom consumer is defined.
        """
        if self._consumer is not None:
            await self._consumer(self)
            return

        await super()._process_output_arcs()

    async def _process_tokens(self) -> bool:
        """
        Calls custom consumer function. If it is ``None`` calls :py:func:`place._process_tokens` function.
        """
        if not await super()._process_tokens():
            return False

        if self._observer is not None:
            """Emulate how it will behave when tokens are sent over an input arc with weight=1."""
            token_count_in_arc = 0
            if self._producer is not None:
                token_count_in_arc = 1
            await self._observe(token_count_in_arc=token_count_in_arc)

        return True

    async def observe(self, token_count_in_arc: int = 0) -> None:
        return
