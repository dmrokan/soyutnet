import asyncio
from typing import (
    Any,
    Tuple,
    Awaitable,
    Callable,
)

from .constants import *
from .pt_common import PTCommon, Arc
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
        self._observer: Observer
        if observer is not None:
            self._observer = observer
            self._observer._set_place(self)

    async def _observe(self, requester: str = "") -> None:
        """
        Save token counts for each label to the observer's records.

        Also, add the number of tokens sent to the caller arc.

        :param token_count_in_arc: Number of tokens in the output arc of places must also be added to the count.
        """
        if self._observer is not None:
            await self._observer.save(requester=requester)


class SpecialPlace(Place):
    """
    Custom place class whose token processing methods can be overriden.
    """

    def __init__(
        self,
        name: str = "",
        consumer: Callable[["SpecialPlace"], Awaitable[None]] | None = None,
        producer: Callable[["SpecialPlace"], Awaitable[list[TokenType]]] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Constructor.

        :param name: Name of the place.
        :param consumer: Custom :py:func:`soyutnet.pt_common.PTCommon._process_input_arcs` function.
        :param producer: Custom :py:func:`soyutnet.pt_common.PTCommon._process_output_arcs` function.
        """
        super().__init__(name=name, **kwargs)
        self._consumer: Callable[["SpecialPlace"], Awaitable[None]] | None = consumer
        """Custom :py:func:`soyutnet.pt_common.PTCommon._process_input_arcs` function."""
        self._producer: (
            Callable[["SpecialPlace"], Awaitable[list[TokenType]]] | None
        ) = producer
        """Custom :py:func:`soyutnet.pt_common.PTCommon._process_output_arcs` function."""

    async def _process_input_arcs(self) -> bool:
        """
        Calls custom producer function after the default
        :py:func:`soyutnet.pt_common.PTCommon._process_input_arcs`.

        :return: If ``True`` continues to processing tokens and output arcs, else loops back to processing input arcs.
        """
        result: bool = await super()._process_input_arcs()
        if self._producer is not None:
            tokens: list[TokenType] = await self._producer(self)
            if tokens:
                for token in tokens:
                    label: label_t = token[0]
                    count: int = self._put_token(token, strict=False)
                    if self._observer is not None:
                        await self._observer.inc_token_count(label)

                return True

        return result

    async def _process_output_arcs(self) -> None:
        """
        Handles consumer function first, if it is defined.

        See, :py:func:`soyutnet.place.Place._process_output_arcs`.
        """
        if self._consumer is not None:
            await self._consumer(self)

        await super()._process_output_arcs()

    async def _process_tokens(self) -> bool:
        """
        Calls custom consumer function. If it is ``None`` calls :py:func:`soyutnet.pt_common.PTCommon._process_tokens` function.
        """
        if not await super()._process_tokens():
            return False

        if self._observer is not None:
            await self._observe(self._name)

        return True

    async def observe(self, requester: str = "") -> None:
        return
