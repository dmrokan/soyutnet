import weakref
from weakref import ReferenceType
from typing import (
    Tuple,
    Never,
    Dict,
    TYPE_CHECKING,
)

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


class BaseObject(object):
    """
    Base SoyutNet object inherited by all classes.
    """

    def __init__(self, net: "SoyutNet") -> None:
        self._net: ReferenceType["SoyutNet"] = weakref.ref(net)
        self._ident: str = ""
        """Every object should have a unique string identifier."""

    @property
    def net(self) -> "SoyutNet":
        """
        Reference of the SoyutNet instance assigned to instances of all object types.
        """
        return self._net()  # type: ignore[return-value]


class SoyutNetError(Exception):
    """
    Generic error class left as future work.
    """

    def __init__(self, message: str = "An error occured.") -> None:
        self.message: str = message
        super().__init__(self.message)
