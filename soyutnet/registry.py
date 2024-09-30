import os
import asyncio
from typing import (
    Any,
    Dict,
    Callable,
    Awaitable,
    Generator,
    Tuple,
    Coroutine,
)

from .constants import *
from .pt_common import PTCommon, _loop
from .observer import Observer, ObserverRecordType, MergedRecordsType
from .token import Token
from .place import Place, SpecialPlace
from .transition import Transition

DirectoryType = Dict[label_t, list[Tuple[id_t, Any]]]
"""Registry directory type"""
PostRegisterCallbackType = Callable[[id_t, Any], None]
"""Type of callbacks run after an object is registered"""


def _default_post_register_callback(dummy1: Any, dummy2: int) -> None:
    """Default dummy :py:attr:`soyutnet.registry.PostRegisterCallbackType`"""
    pass


class Registry(BaseObject):
    """
    Registry keeps track of (label, id) tuples and the objects assigned to them.
    It generates unique ids for new objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._id_counter: id_t = INITIAL_ID
        """Auto-incrementing id assigned to new objects"""
        self._directory: DirectoryType = {}
        """Keeps all objects categorized by labels"""
        self._lock: asyncio.Lock = asyncio.Lock()
        """Locks access to :py:attr:`soyutnet.registry.Registry._directory`"""

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

    def get_entry_count(self, label: label_t = GENERIC_LABEL) -> int:
        """
        Returns the number of entries with the given label.

        :param label: Label.
        :return: Number of entries.
        """
        if label in self._directory:
            return len(self._directory)

        return 0

    def get_first_entry(self, label: label_t = GENERIC_LABEL) -> Tuple[id_t, Any]:
        """
        Returns first entry with given label. First entry is the one registered first.

        :param label: Label.
        :return: Entry.
        """
        if label in self._directory and len(self._directory[label]) > 0:
            return self._directory[label][0]

        return (INVALID_ID, None)

    def get_entry(
        self, label: label_t, id: id_t | None = None, del_entry: bool = False
    ) -> Any:
        """
        Returns a token with given label and ID.

        :param label: Label.
        :param id: ID. If ``None``, returns the first entry with the given label.
        :param del_entry: Removes the entry from the registry if ``True``.
        :return: The registered token.
        """
        result: Any = None
        if label not in self._directory:
            return result

        i: int = 0
        for entry in self._directory[label]:
            if id is None or entry[0] == id:
                result = entry[1]
                if del_entry:
                    del self._directory[label][i]
                break
            i += 1

        return result

    def pop_entry(self, label: label_t, id: id_t | None = None) -> Any:
        """
        Returns a token with given label and ID and removes it from the registry.

        :param label: Label.
        :param id: ID. If ``None``, returns the first entry with the given label.
        :return: The registered token.
        """
        return self.get_entry(label, id, del_entry=True)

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


class TokenRegistry(Registry):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def register(self, token: Token) -> id_t:  # type: ignore[override]
        """
        Register a new token

        :param token: New token.
        :return: Assigned unique ID.
        """

        def callback(new_id: id_t, tkn: Any) -> None:
            tkn._id = new_id

        return super().register(token, callback)


class PTRegistry(Registry):
    """
    Keeps track of PTCommon instances.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Constructor.
        """
        super().__init__(**kwargs)

    def get_loops(self) -> Generator[Coroutine[Any, Any, None], None, None]:
        """
        Yields asyncio task functions assigned to the PT.

        :return: Asyncio task function.
        """
        for label in self._directory:
            for entry in self._directory[label]:
                yield _loop(entry[1])

    def register(self, pt: PTCommon) -> id_t:  # type: ignore[override]
        """
        Registers a PT.

        :param pt: PTCommon instance.
        :return: Unique ID assigned to the PT.
        """

        def callback(new_id: id_t, pt: PTCommon) -> None:
            pt._id = new_id
            if not pt._name:
                class_name: str = type(pt).__name__
                if isinstance(pt, Place):
                    pt._name = f"p{pt._id}"
                elif isinstance(pt, Transition):
                    pt._name = f"t{pt._id}"
            self.net.DEBUG_V(f"Registered: {pt.ident()}")

        return super().register(pt, callback)

    def get_merged_records(
        self,
        ignore_special_places: bool = True,
        place_names: list[str] = [],
    ) -> MergedRecordsType:
        """
        TODO
        Merges all observer records and sorts by their timestamps.

        :return: Merged and sorted observer records.
        """
        output: list[Tuple[str, ObserverRecordType | Tuple[float]]] = []
        for e in self.entries():
            obj: Any = e[1]
            if not isinstance(obj, PTCommon):
                continue
            if ignore_special_places and isinstance(obj, SpecialPlace):
                continue
            name: str = obj._name
            if place_names and name not in place_names:
                continue
            if obj._observer is None:
                continue
            obsv: Observer = obj._observer
            for record in obsv.get_records():
                output.append((name, record))

        return sorted(output, key=lambda rec: rec[1][0])

    def _get_graphviz_node_definition(self, pt: PTCommon, t: int) -> str:
        shape: str = "circle"
        color: str = "#000000"
        fillcolor: str = "#dddddd"
        height: float = 1
        width: float = 1
        fontsize: int = 20
        penwidth: int = 3
        style: str = "filled"
        if isinstance(pt, Transition):
            shape = "box"
            color = "#cccccc"
            fillcolor = "#000000"
            height = 0.25
            width = 1.25
        elif isinstance(pt, SpecialPlace):
            fillcolor = "#777777"
        node_fmt: str = (
            """{}_{} [shape="{}",fontsize="{}",style="{}",color="{}",fillcolor="{}",label="",xlabel="{}",height="{}",width="{}",penwidth={}];"""
        )

        return node_fmt.format(
            pt._name,
            t,
            shape,
            fontsize,
            style,
            color,
            fillcolor,
            pt._name,
            height,
            width,
            penwidth,
        )

    def generate_graph(
        self,
        net_name: str = "Net",
        indent: str = "\t",
        label_names: Dict[label_t, str] = {},
    ) -> str:
        eol: str = os.linesep
        gv: str = f"digraph {net_name} {{" + eol
        gv_nodes: str = ""
        gv_arcs: str = ""
        for e in self.entries():
            obj: Any = e[1]
            if not isinstance(obj, PTCommon):
                continue
            node_def: str = self._get_graphviz_node_definition(obj, 0)
            gv_nodes += 2 * indent + node_def + eol
            for arc in obj._input_arcs:
                gv_arcs += (
                    2 * indent
                    + arc.get_graphviz_definition(t=0, label_names=label_names)
                    + eol
                )

        gv += indent + "subgraph cluster_0 {" + eol
        gv += gv_nodes
        gv += gv_arcs
        gv += indent + "}" + eol
        gv += indent + "clusterrank=none;" + eol
        gv += "}" + eol

        return gv
