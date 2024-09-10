import asyncio
from typing import (
    Any,
    Dict,
    Callable,
    Awaitable,
    Generator,
    Tuple,
)

from .global_defs import *
from . import common as _c

DirectoryType = Dict[label_t, list[Tuple[id_t, Any]]]
PostRegisterCallbackType = Callable[[id_t, Any], None]


def _default_post_register_callback(dummy1: Any, dummy2: int) -> None:
    pass


class Registry(object):
    """
    Registry keeps track of (label, id) tuples and the objects assigned to them.
    It generates unique ids for new objects.
    """

    def __init__(self) -> None:
        self._id_counter: id_t = _c.INITIAL_ID
        """Auto-incrementing id assigned to new objects"""
        self._directory: DirectoryType = {}
        """Keeps all objects categorized by labels"""
        self._lock: asyncio.Lock = asyncio.Lock()
        """Locks access to :py:attr:`self._directory`"""

    def _new_id(self) -> id_t:
        """
        Creates new ids for new objects.

        :return: Unique id
        """
        self._id_counter += 1
        return self._id_counter

    def register(
        self,
        obj: Any,
        post_register_callback: PostRegisterCallbackType = _default_post_register_callback,
    ) -> id_t:
        """
        Register a new object

        :param obj: New object of any type.
        :param post_register_callback: Called after object is registered.
        :return: Assigned unique ID.
        """
        new_id: id_t = self._new_id()
        label: label_t = obj.get_label()
        if label not in self._directory:
            self._directory[label] = []
        self._directory[label].append((new_id, obj))
        if post_register_callback != _default_post_register_callback:
            post_register_callback(new_id, obj)

        return new_id

    def get_entry_count(self, label: label_t = _c.GENERIC_LABEL) -> int:
        """
        Returns the number of entries with the given label.

        :param label: Label.
        :return: Number of entries.
        """
        if label in self._directory:
            return len(self._directory)

        return 0

    def get_first_entry(self, label: label_t = _c.GENERIC_LABEL) -> Tuple[id_t, Any]:
        """
        Returns first entry with given label. First entry is the one registered first.

        :param label: Label.
        :return: Entry.
        """
        if label in self._directory and len(self._directory[label]) > 0:
            return self._directory[label][0]

        return (_c.INVALID_ID, None)

    def get_entries(self, label: label_t, id: id_t) -> list[Any]:
        """
        Returns a list of objects with given label and ID.

        :param label: Label.
        :param id: ID.
        :return: A list of objects.
        """
        result: list[Any] = []
        if label not in self._directory:
            return result

        for entry in self._directory[label]:
            if entry[0] == id:
                result.append(entry[1])

        return result

    def entries(self, label: label_t | None = None) -> Generator[Any, None, None]:
        """
        Iterates through all entries with the given label.

        :param label: Label. If it is ``None``, iterates through all labels.
        :return: Yields entries
        """
        d: DirectoryType = (
            {label: self._directory[label]}
            if label in self._directory
            else self._directory
        )
        for label in d:
            for entry in d[label]:
                yield entry
