from typing import (
    Tuple,
    Never,
    Dict,
)

LOOP_DELAY = 0.0
"""Asyncio tasks main loop delay. It can be picked a positive number for debugging."""
DEBUG_ENABLED = False
"""if set, :py:func:`soyutnet.common.DEBUG` will print."""
VERBOSE_ENABLED = False
"""if set, :py:func:`soyutnet.common.DEBUG_V` will print."""

SLOW_MOTION = False
"""If set, :py:attr:`soyutnet.global_defs.LOOP_DELAY` will be ``0.5``"""

label_t = int
id_t = int

if SLOW_MOTION:
    LOOP_DELAY = 0.5

TokenType = Tuple[label_t, id_t] | Tuple[Never, ...]
TokenWalletType = Dict[label_t, list[id_t]]
