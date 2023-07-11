from __future__ import annotations

from asyncio import Lock, Event, Semaphore, sleep
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Coroutine, Final, Literal, Optional, Tuple, TypeAlias, Union

    DateLike: TypeAlias = Union[
        str,
        int,
        float,
        datetime,
    ]

__all__: Tuple[str, ...] = (
    'SnowflakeGenerator',
)

EKO_EPOCH: Final[datetime] = datetime(
    year = 2019,
    month = 4,
    day = 15,
    hour = 4,
    minute = 12,
)

def snowflake_to_datetime(
    snowflake: int,
    epoch: datetime,
) -> datetime:
    """
    Convert a snowflake ID to a datetime object.

    Parameters
    ----------

        snowflake: :class:`int`
            The snowflake ID to convert.

        epoch: datetime
            The epoch datetime value used during snowflake ID creation.

    Returns
    -------
        :class:`datetime`
            The datetime object from the snowflake ID.

    """

    return datetime.fromtimestamp(((snowflake >> 22) + int(epoch.timestamp() * 1000)) / 1000)

async def generate_snowflake(
    epoch: datetime = EKO_EPOCH,
    worker_id: Optional[int] = 0,
    process_id: Optional[int] = 0,
    *,
    last_timestamp: Optional[datetime] = datetime.now(),
    sequence: Optional[int] = 0,
) -> Tuple[int, datetime, int]:
    """
    Generates a snowflake ID based on the provided parameters.

    Parameters
    ----------

        epoch: :class:`int`
            The epoch timestamp to use for the snowflake.

        worker_id: Optional[:class:`int`]
            The worker ID to use for the snowflake.

        process_id: Optional[:class:`int`]
            The process ID to use for the snowflake.

        last_timestamp: Optional[:class:`int`]
            The last timestamp used for the snowflake. Defaults
            to `0`.

        sequence: Optional[:class:`int`]
            The sequence to use for the snowflake. Defaults to
            `0`.

    Returns
    -------
        :class:`int`
            The generated snowflake ID.

    """
    now  = datetime.utcnow()

    while True:
        now  = datetime.utcnow()

        if last_timestamp > now: # type: ignore[operator]
            # moving backwards in time
            await sleep((last_timestamp - now).total_seconds()) # type: ignore[operator]
            continue

        if last_timestamp == now:
            sequence = (sequence + 1) & 4095  # type: ignore[operator]

            if sequence == 0:
                await sleep(1/1000)
                continue
        else:
            sequence = 0

        break

    return ((
        (int((now.timestamp() * 1000) - (epoch.timestamp() * 1000)) << 22) |
        (worker_id << 17) |  # type: ignore[operator]
        (process_id << 12) |  # type: ignore[operator]
        sequence
    ), now, sequence)

class SnowflakeGenerator:
    if TYPE_CHECKING:
        __lock: Lock
        _frozen: bool
        _locked: Event
        _unlocked: Event
        _counter: Semaphore
        _sequence: int
        _last_timestamp: datetime
        epoch: datetime
        worker_id: int
        process_id: int

    __slots__: Tuple[str, ...] = (
        '__lock',
        '_frozen',
        '_locked',
        '_unlocked',
        '_counter',
        '_sequence',
        '_last_timestamp',
        'name',
        'epoch',
        'worker_id',
        'process_id',
    )

    def __init__(
        self: SnowflakeGenerator,
        epoch: Optional[datetime] = EKO_EPOCH,
        *,
        worker_id: Optional[int] = 0,
        process_id: Optional[int] = 0,
    ) -> None:
        self._frozen = False
        self.__lock = Lock()
        self._locked = Event()
        self._unlocked = Event()
        self._counter = Semaphore(0)
        self._sequence = 0
        self._last_timestamp = datetime.now()

        self._setup(
            epoch,
            worker_id,
            process_id,
        )

    def _set_epoch(
        self,
        epoch: Optional[datetime] = EKO_EPOCH,
    ) -> None:
        if self.frozen:
            raise RuntimeError(
                f"'{type(self).__name__}._set_epoch()' can only be "
                "called once per instance, and cannot be called "
                f"after '{type(self).__name__}._setup()' has been called."
            )

        epoch_type = type(epoch)

        if not isinstance(epoch, datetime):
            if isinstance(epoch, str):
                try:
                    epoch = datetime.fromisoformat(epoch)
                except ValueError:
                    epoch = epoch.replace(',', '')

                if '.' in epoch:
                    epoch = float(epoch)

            if isinstance(epoch, int):
                epoch = float(epoch / 1000)

            if isinstance(epoch, float):
                epoch = datetime.fromtimestamp(epoch)

        if not isinstance(epoch, datetime):
            raise TypeError(
                f"'{type(self).__name__}._set_epoch()' 'epoch' "
                "value must be an instance of 'int', 'float', or "
                f"'datetime'; received an instance of {epoch_type.__name__!r}"
            )

        self.epoch = epoch # type: ignore[arg-type]

    def _set_worker_id(
        self,
        worker_id: Optional[int] = 0,
    ) -> None:
        if self.frozen:
            raise RuntimeError(
                f"'{type(self).__name__}._set_worker_id()' can only be "
                "called once per instance, and cannot be called "
                f"after '{type(self).__name__}._setup()' has been called."
            )

        if not isinstance(worker_id, int):
            raise TypeError(
                f"'{type(self).__name__}._set_worker_id()' 'worker_id' "
                "value must be an instance of 'int'; received an instance"
                f" of {type(worker_id).__name__!r}"
            )

        self.worker_id = worker_id # type: ignore[arg-type]

    def _set_process_id(
        self,
        process_id: Optional[int] = 0,
    ) -> None:
        if self.frozen:
            raise RuntimeError(
                f"'{type(self).__name__}._set_process_id()' can only be "
                "called once per instance, and cannot be called "
                f"after '{type(self).__name__}._setup()' has been called."
            )

        if not isinstance(process_id, int):
            raise TypeError(
                f"'{type(self).__name__}._set_process_id()' 'process_id' "
                "value must be an instance of 'int'; received an instance"
                f" of {type(process_id).__name__!r}"
            )

        self.process_id = process_id # type: ignore[arg-type]

    def _setup(
        self: SnowflakeGenerator,
        epoch: Optional[datetime] = EKO_EPOCH,
        worker_id: Optional[int] = 0,
        process_id: Optional[int] = 0,
    ) -> None:
        if self.frozen:
            raise RuntimeError(
                f"'{type(self).__name__}._setup() can only be called "
                "once per instance."
            )

        self._set_epoch(epoch)
        self._set_worker_id(worker_id)
        self._set_process_id(process_id)
        self._frozen = True

    def __repr__(self: SnowflakeGenerator) -> str:
        if not self.frozen:
            return f"<{type(self).__name__} setup={False!r}>"

        return (
            f"<SnowflakeGenerator epoch={self.epoch!r} worker_id"
            f"={self.worker_id!r} process_id={self.process_id!r}"
            f" counter={self._counter._value:,}>"
        )

    def __str__(self: SnowflakeGenerator) -> str:
        return self.__repr__()

    def __bool__(self: SnowflakeGenerator) -> bool:
        return self.frozen and self.unlocked

    async def generate(self: SnowflakeGenerator) -> int:
        if not self.frozen:
            raise RuntimeError(
                f"'{type(self).__name__}.generate()' cannot be called "
                "before '{type(self).__name__}._setup()' has been called"
            )

        await self._lock()

        _id, self._last_timestamp, self._sequence = await generate_snowflake(
            self.epoch,
            self.worker_id,
            self.process_id,
            last_timestamp = self._last_timestamp,
            sequence = self._sequence,
        )

        self._counter.release()
        self._unlock()

        return _id

    def __call__(self: SnowflakeGenerator) -> Coroutine[Any, Any, int]:
        if not self.frozen:
            raise RuntimeError(
                f"{type(self).__name__!r} cannot be called "
                "before '{type(self).__name__}._setup()' has been called"
            )

        return self.generate()

    def __aiter__(self: SnowflakeGenerator) -> SnowflakeGenerator:
        if not self.frozen:
            raise RuntimeError(
                f"'{type(self).__name__}.__aiter__()' cannot be called "
                "before '{type(self).__name__}._setup()' has been called"
            )

        return self

    def __anext__(self: SnowflakeGenerator) -> Coroutine[Any, Any, int]:
        if not self.frozen:
            raise RuntimeError(
                f"'{type(self).__name__}.__anext__()' cannot be called "
                "before '{type(self).__name__}._setup()' has been called"
            )

        return self.__call__()

    @property
    def frozen(self: SnowflakeGenerator) -> bool:
        return self._frozen

    @property
    def locked(self: SnowflakeGenerator) -> bool:
        return self.__lock.locked()

    @property
    def unlocked(self: SnowflakeGenerator) -> bool:
        return not self.__lock.locked()

    def to_datetime(
        self,
        snowflake: int,
    ) -> datetime:
        return snowflake_to_datetime(
            snowflake,
            self.epoch,
        )

    async def _lock(self: SnowflakeGenerator) -> None:
        if not self.frozen:
            raise RuntimeError(
                f"'{type(self).__name__}._lock()' cannot be called "
                "before '{type(self).__name__}._setup()' has been called"
            )

        if self.locked:
            raise RuntimeError("Cannot lock while already locked")

        await self.__lock.acquire()
        self._unlocked.clear()
        self._locked.set()

    def wait_locked(self: SnowflakeGenerator) -> Coroutine[Any, Any, Literal[True]]:
        if not self.frozen:
            raise RuntimeError(
                f"'{type(self).__name__}.wait_locked()' cannot be called "
                "before '{type(self).__name__}._setup()' has been called"
            )

        return self._locked.wait()

    def _unlock(self: SnowflakeGenerator) -> None:
        if not self.frozen:
            raise RuntimeError(
                f"'{type(self).__name__}._unlock()' cannot be called "
                "before '{type(self).__name__}._setup()' has been called"
            )

        if self.unlocked:
            raise RuntimeError("Cannot unlock while not locked")

        self.__lock.release()
        self._locked.clear()
        self._unlocked.set()

    def wait_unlocked(self: SnowflakeGenerator) -> Coroutine[Any, Any, Literal[True]]:
        if not self.frozen:
            raise RuntimeError(
                f"'{type(self).__name__}.wait_unlocked()' cannot be called "
                "before '{type(self).__name__}._setup()' has been called"
            )

        return self._unlocked.wait()
