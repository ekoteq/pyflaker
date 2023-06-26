from __future__ import annotations

from typing import TYPE_CHECKING
from time import sleep
from datetime import datetime

from .constants import EKO_EPOCH_TIMESTAMP_MS
from .utilities import timestamp

if TYPE_CHECKING:
    from typing import Any, Type, Tuple, Optional, Mapping

__all__: Tuple[str, ...] = (
    'SnowflakeGenerator',
)

class SnowflakeGeneratorMeta(type):
    """
    A metaclass for creating Snowflake Generators.

    Allows defining the epoch, process ID, and worker ID
    of the snowflake generator during metaclass assignment.
    """
    if TYPE_CHECKING:
        _epoch: int
        _process_id: int
        _worker_id: int
        _last_timestamp: int
        _sequence: int

    def __new__(
        mcls: Type[SnowflakeGeneratorMeta],
        name: str,
        bases: Tuple[Type[Any], ...],
        namespace: Mapping[str, Any],
        *args: Any,
        epoch: Optional[int] = None,
        process_id: Optional[int] = None,
        worker_id: Optional[int] = None,
        **kwargs: Any,
    ) -> SnowflakeGenerator:
        if epoch is not None:
            namespace['_epoch'] = epoch

        if process_id is not None:
            namespace['_process_id'] = process_id

        if worker_id is not None:
            namespace['_worker_id'] = worker_id

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
            *args,
            **kwargs,
        )

class SnowflakeGenerator(metaclass = SnowflakeGeneratorMeta, epoch = EKO_EPOCH_TIMESTAMP_MS):
    """
    A class used to generate snowflake IDs.

    """
    if TYPE_CHECKING:
        _epoch: int
        _process_id: int
        _worker_id: int
        _last_timestamp: int
        _sequence: int

    __slots__: Tuple[str, ...] = (
        '_epoch',
        '_process_id',
        '_worker_id',
        '_last_timestamp',
        '_sequence',
    )

    def __init__(
        self,
        process_id: Optional[int] = 0,
        worker_id: Optional[int] = 0,
    ) -> None:
        """
        Parameters
        ----------
        increment : int
            The increment of the snowflake generator.

        process_id : int
            The process ID of the snowflake generator.

        worker_id : int
            The worker ID of the snowflake generator.
        """
        self._process_id = process_id
        self._worker_id = worker_id
        self._last_timestamp = -1
        self._sequence = 0

    def generate(self) -> int:
        """
        Generates a snowflake ID.

        This is an alias for `next(generator)`.

        Parameters
        ----------
        timestamp : int
            The timestamp to use for the snowflake ID.

        Returns
        -------
        int
            The snowflake ID.
        """
        now = -1

        while True:
            now = timestamp()

            if now < self._last_timestamp:
                sleep(1/1000)
                continue

            if now == self._last_timestamp:
                self._sequence = (self._sequence + 1) & 0xFFF

                if self._sequence == 0:
                    sleep(1/1000)
                    continue
            else:
                self._sequence = 0

            self._last_timestamp = now
            break

        return (
            ((now - self._epoch) << 22)
            | (self._worker_id << 17)
            | (self._process_id << 12)
            | self._sequence
        )

    def __iter__(self) -> SnowflakeGenerator:
        """
        Returns
        -------
        SnowflakeGenerator
            The snowflake generator.
        """
        return self

    def __next__(self) -> int:
        """
        Generates a snowflake ID.

        This is an alias for `generator.generate()`.

        Returns
        -------
        int
            The snowflake ID.
        """
        return self.generate()

    @property
    def epoch(self) -> int:
        """
        Returns
        -------
        int
            The epoch of the snowflake generator.
        """
        return self._epoch

    @property
    def process_id(self) -> int:
        """
        Returns
        -------
        int
            The process ID of the snowflake generator.
        """
        return self._process_id

    @property
    def worker_id(self) -> int:
        """
        Returns
        -------
        int
            The worker ID of the snowflake generator.
        """
        return self._worker_id

    @property
    def last_timestamp(self) -> int:
        """
        Returns
        -------
        int
            The last timestamp of the snowflake generator.
        """
        return self._last_timestamp

    @property
    def sequence(self) -> int:
        """
        Returns
        -------
        int
            The sequence of the snowflake generator.
        """
        return self._sequence
