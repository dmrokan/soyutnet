import random
import string
import weakref
from weakref import ReferenceType
from typing import (
    Any,
    Tuple,
    Dict,
    TYPE_CHECKING,
)

try:
    from typing import Never
except ImportError:
    """Never requires python>=3.11"""
    Never = Any

label_t = int
"""Label type"""
id_t = int
"""ID type"""
TokenType = Tuple[label_t, id_t] | Tuple[Never, ...]
"""Token type"""
TokenWalletType = Dict[label_t, list[id_t]]
"""Token container type"""

if TYPE_CHECKING:
    from . import SoyutNet

INVALID_LABEL: label_t = -10
"""Invalid label"""
INVALID_ID: id_t = -11
"""Invalid id"""
GENERIC_LABEL: label_t = 0
"""Generic label"""
GENERIC_ID: id_t = 0
"""Generic ID"""
INITIAL_ID: id_t = 0


def random_identifier(N: int = 5) -> str:
    return "".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(N)
    )


class BaseObject(object):
    """
    Base SoyutNet object inherited by all classes.
    """

    def __init__(self, net: "SoyutNet") -> None:
        self._net: ReferenceType["SoyutNet"] = weakref.ref(net)
        """Reference to the creator SoyutNet instance."""
        self._ident0: str = random_identifier()

    @property
    def net(self) -> "SoyutNet":
        """
        Get reference of the SoyutNet instance assigned to instances of all object types,
        for a particular simulation.

        :return: Reference to the creator SoyutNet instance.
        """
        return self._net()  # type: ignore[return-value]

    def ident(self) -> str:
        """
        Get object's unique identifier

        :return: Identifier string.
        """
        return self._ident0


class SoyutNetError(Exception):
    """
    Generic error class left as future work.
    """

    def __init__(self, message: str = "An error occured.") -> None:
        self.message: str = message
        super().__init__(self.message)
