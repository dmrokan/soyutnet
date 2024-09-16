import asyncio
from typing import Any

from .constants import *


class Token(BaseObject):
    def __init__(
        self, label: label_t = GENERIC_LABEL, binding: Any = None, **kwargs: Any
    ) -> None:
        """
        A class that represents a labeled PTNet token which can be binded to any object.

        :param label: Label.
        :param binding: Binded object.
        """
        super().__init__(**kwargs)
        self._label: label_t = label
        """Token label"""
        self._id: id_t = GENERIC_ID
        """Unique token ID"""
        self._binding: Any = binding
        """Binded object"""

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
