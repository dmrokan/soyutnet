import asyncio
from typing import (
    Any,
    Dict,
)

from .global_defs import *
from . import common as _c
from .pt_common import PTCommon, PTRegistry


class Transition(PTCommon):
    """
    Defines PTNet transitions.
    """

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        """
        Constructor.

        :param name: Name of the transition.
        """
        super().__init__(name=name, **kwargs)
        self._no_of_times_enabled: int = 0
        """Counts the number of time the transition is enabled"""

    async def _process_input_arcs(self) -> bool:
        """
        Acquires and stores tokens.

        :return: ``True`` if the transition is enabled, else goes back to waiting input arcs to be enabled.
        """
        _c.DEBUG_V(f"{self._ident}: process_input_arcs")
        async for arc in self._get_input_arcs():
            if not arc.is_enabled():
                return False

        _c.DEBUG_V(f"Enabled!")
        self._no_of_times_enabled += 1

        async for arc in self._get_input_arcs():
            await arc.observe_input_places()
            count: int = arc.weight
            async for token in arc.wait():
                _c.DEBUG_V(f"Received '{token}' from {arc}")
                self._put_token(token)
                count -= 1
                if count <= 0:
                    break

        return True

    async def _process_tokens(self) -> bool:
        """
        Calls ``super()``'s version.

        See, :py:func:`soyutnet.pt_common.PTCommon._process_tokens`.
        """
        return await super()._process_tokens()

    async def _process_output_arcs(self) -> None:
        """
        Fires the transition.

        NOTE: sum of w(p_prev, self) == sum of w(self, p_next) must satisfy for each label.

        Sends tokens to the output places when required conditions are satisfied.
        """
        _c.DEBUG_V(f"{self._ident}: process_output_arcs")
        async for arc in self._get_output_arcs():
            count: int = arc.weight
            while count > 0:
                token: TokenType = tuple()
                for label in arc.labels:
                    token = self._get_token(label)
                    if token:
                        break
                if not token:
                    break
                _c.DEBUG_V(f"Sending '{token}' to {arc}")
                await arc.send(token)
                count -= 1

    def get_no_of_times_enabled(self) -> int:
        """
        Returns number of times the transition is enabled.

        :return: Number of times the transition is enabled.
        """
        return self._no_of_times_enabled
