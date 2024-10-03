import asyncio
from typing import (
    Any,
    Dict,
)

from .constants import *
from .pt_common import PTCommon

FiringRecordType = Tuple[float]
"""Firing record type"""
FiringHistoryType = list[FiringRecordType]
"""Type for list of firing records"""


class Transition(PTCommon):
    """
    Defines PTNet transitions.
    """

    def __init__(
        self, name: str = "", record_firing: bool = False, **kwargs: Any
    ) -> None:
        """
        Constructor.

        :param name: Name of the transition.
        """
        super().__init__(name=name, **kwargs)
        self._no_of_times_enabled: int = 0
        """Counts the number of time the transition is enabled"""
        self._firing_records: FiringHistoryType = []
        """Keeps timestampts of each firing of the transition: py:attr:`soyutnet.transition.FiringRecordType`"""
        self._record_firing: bool = record_firing
        """Enables recording firings of transitions"""
        self._notifier: asyncio.Condition = asyncio.Condition()
        """Firing notifier"""

    def _new_firing_record(self) -> None:
        self._firing_records.append((self.net.time(),))

    async def _process_input_arcs(self) -> bool:
        """
        Acquires and stores tokens.

        :return: ``True`` if the transition is enabled, else goes back to waiting input arcs to be enabled.
        """
        self.net.DEBUG_V(f"{self.ident()}: process_input_arcs")
        async for arc in self._get_input_arcs():
            if not arc.is_enabled():
                return False

        self.net.DEBUG_V(f"Enabled!")
        self._no_of_times_enabled += 1
        if self._record_firing:
            self._new_firing_record()

        async with self._notifier:
            self._notifier.notify_all()

        async for arc in self._get_input_arcs():
            await arc.observe_input_places(self._name)
            count: int = arc.weight
            async for token in arc.wait():
                self.net.DEBUG_V(f"Received '{token}' from {arc}")
                self._put_token(token)
                await arc.notify_observer(token[0])
                count -= 1
                if count <= 0:
                    break

        return True

    async def _process_output_arcs(self) -> None:
        """
        Fires the transition.

        NOTE: sum of w(p_prev, self) == sum of w(self, p_next) must satisfy for each label.

        Sends tokens to the output places when required conditions are satisfied.
        """
        self.net.DEBUG_V(f"{self.ident()}: process_output_arcs")
        async for arc in self._get_output_arcs():
            count: int = arc.weight
            while count > 0:
                token: TokenType = tuple()
                for label in arc.labels(remember_last_processed=True):
                    token = self._get_token(label)
                    if token:
                        break
                if not token:
                    break
                self.net.DEBUG_V(f"Sending '{token}' to {arc}")
                await arc.send(token)
                count -= 1

    def get_no_of_times_enabled(self) -> int:
        """
        Returns number of times the transition is enabled.

        :return: Number of times the transition is enabled.
        """
        return self._no_of_times_enabled

    def get_firing_records(self) -> FiringHistoryType:
        """
        Returns all firing records. :py:attr:`soyutnet.transition.Transition._firing_records`

        :return: Firing records.
        """
        return self._firing_records

    async def wait_for_firing(self) -> bool:
        async with self._notifier:
            await self._notifier.wait()

        return True
