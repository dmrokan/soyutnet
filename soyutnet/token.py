import asyncio

from typing import (
    Any,
)

from .global_defs import *
from . import common as _c
from .registry import (
    Registry,
)


class Token(object):
    def __init__(self, label: label_t = _c.GENERIC_LABEL, binding: Any = None) -> None:
        """
        A class that represents a labeled PTNet token which can be binded to any object.

        :param label: Label.
        :param binding: Binded object.
        """
        self._label: label_t = label
        """Token label"""
        self._id: id_t = _c.GENERIC_ID
        """Unique token ID"""
        self._binding: Any = binding
        """Binded object"""
        self._ident: str = ""  # TODO: Place ident logic here remove from other parts

    def get_label(self) -> label_t:
        """
        Returns the label of token

        :return: Label.
        """
        return self._label

    def get_binding(self) -> Any:
        """
        Returns the object binded to the token.

        :return: Binded object.
        """
        return self._binding

    def get_id(self) -> id_t:
        """
        Returns token's unique ID.

        :return: ID.
        """
        return self._id


class TokenRegistry(Registry):
    def __init__(self) -> None:
        super().__init__()

    def register(self, token: Token) -> id_t:  # type: ignore[override]
        """
        Register a new token

        :param token: New token.
        :return: Assigned unique ID.
        """

        def callback(new_id: id_t, tkn: Any) -> None:

            tkn._id = new_id

        return super().register(token, callback)
