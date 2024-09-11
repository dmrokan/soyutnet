import asyncio
from typing import (
    Any,
    Dict,
    Tuple,
    Callable,
)

from .global_defs import *
from . import common as _c


ObserverRecordType = Tuple[float, label_t, int]
"""Observer records: (observation time, label, no of tokens with the label)"""
ObserverHistoryType = list[ObserverRecordType]


class Observer(object):
    """
    Can be assigned to a place to observe its state.
    """

    def __init__(
        self, record_limit: int = 0, verbose: bool = False, pt_ident: str = ""
    ) -> None:
        """
        Constructor.

        :param record_limit: Maximum number of records to be kept. It is unlimited if chose ``0``.
        :param verbose: Print observations if ``True``.
        :param pt_ident: Custom identification string that will be used in debug prints.
        """
        self._records: ObserverHistoryType = []
        """Records of observations. A list of triplet (observation_time, token_label, token_count)"""
        self._lock: asyncio.Lock = asyncio.Lock()
        """Async lock for safe access to records"""
        self._record_limit: int = record_limit
        """Maximum number of records to be kept."""
        self._hysteresis_bounds: Tuple[int, int] = (
            int(self._record_limit * 0.91),
            int(self._record_limit * 1.1),
        )
        """Deleting old records are optimized by an hysteresis comparator"""
        self._verbose: bool = verbose
        """Prints the observations if ``True``"""
        self._token_counters: Dict[label_t, int] = {}
        self._ident: str = pt_ident
        """Identication string that will be used in debug prints"""

    async def _clean_records(self) -> int:
        """
        Cleans records when it is required.

        :return: Number of records kept after cleaning the old ones.
        """
        count: int = -1
        if self._record_limit > 0:
            async with self._lock:
                count = len(self._records)
                if count >= self._hysteresis_bounds[1]:
                    self._records = self._records[count - self._hysteresis_bounds[0] :]
                    count = len(self._records)

        return count

    def _add_record(self, record: ObserverRecordType) -> int:
        """
        Adds a new record.

        :param record: Record.
        :return: Number of records.
        """
        self._records.append(record)

        return len(self._records)

    async def _display_records(self) -> None:
        """
        Print records to the stdout.
        """
        output: str = f"{self._ident} has {len(self._records)} records\n"
        for record in self._records:
            output += f"  {record}\n"

        _c.DEBUG(output)

    async def _save(self, record: ObserverRecordType) -> None:
        """
        Save a new record.

        :param record: Record.
        """
        if self._verbose:
            _c.DEBUG(f"REC: {self._ident}:", record)
        self._add_record(record)
        await self._clean_records()

    async def save(self, token_count_in_arc: int = 0) -> None:
        """
        Save counted tokens to the list of records.

        It is called by output transitions when they are enabled.

        :param token_count_in_arc: Number of tokens in the output arc of places must also be added to the count.
        """
        async with self._lock:
            for label in self._token_counters:
                time: float = _c.time()
                record: ObserverRecordType = (
                    time,
                    label,
                    self._token_counters[label] + token_count_in_arc,
                )
                await self._save(record)
                self._token_counters[label] = 0

    def get_records(self, column: int = -1) -> list[Any]:
        """
        Returns the records at the specified column.

        :param column: The column index of records requested. It returns all columns if it it ``-1``.
        :return: List of records.
        """
        if column < 0:
            return self._records

        output: list[Any] = []
        for rec in self._records:
            output.append(rec[column])

        return output

    async def inc_token_count(self, label: label_t, inc: int = 1) -> None:
        """
        Adds to the token count with the given label.

        It is called by places when a new token acquired or sent.

        :param label: Token label.
        :param inc: The value to be added to the count.
        """
        async with self._lock:
            if label not in self._token_counters:
                self._token_counters[label] = 0
            self._token_counters[label] += inc


class ComparativeObserver(Observer):
    """
    This observer compares the records to the provided list for test purposes.
    """

    def __init__(
        self,
        expected: Dict[int, list[Any]],
        on_comparison_ends: Callable[["ComparativeObserver"], None] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Constructor.

        :param expected: Values to be compared to.
        :param on_comparison_ends: Callback function to be called when all values in :py:attr:`self.expected` are used.
        """
        super().__init__(**kwargs)
        self._expected: Dict[int, list[Any]] = expected
        """The list of values to be compared to"""
        self._expected_index: int = 0
        """Index of the last value compared in the list"""
        self._is_still_comparing: bool = True
        """Set to ``False`` when there are no values left to compare in :py:attr:`self._expected`"""
        self._on_comparison_ends: Callable[["ComparativeObserver"], None] | None = (
            on_comparison_ends
        )
        """Callback function to be called when comparison ends"""

    async def _save(self, record: ObserverRecordType) -> None:
        """
        Save a new record after comparing.

        :param record: Record.
        :return: Number of records.
        """
        if self._is_still_comparing:
            column_count: int = 0
            for column in self._expected:
                if len(self._expected[column]) <= self._expected_index:
                    continue
                value: Any = self._expected[column][self._expected_index]
                if value >= 0 and record[column] != value:
                    raise RuntimeError(
                        f"{self._ident}: actual ({column}, {record[column]}) =/= expected ({column}, {value})"
                    )
                else:
                    _c.DEBUG_V(f"({column}, {record[column]}) == ({column}, {value})")

                if len(self._expected[column]) - 1 >= self._expected_index:
                    column_count += 1

            self._expected_index += 1
            if column_count == 0:
                self._is_still_comparing = False
                if self._verbose:
                    await self._display_records()
                if self._on_comparison_ends is not None:
                    _c.DEBUG("comparison ends")
                    self._on_comparison_ends(self)

        if self._verbose:
            _c.DEBUG(f"REC: {self._ident}:", record)
        self._add_record(record)
