from __future__ import annotations

from datetime import datetime
from time import sleep
from threading import (
    Event,
    Lock,
)
from typing import (
    TYPE_CHECKING,
    Generic,
    TypeVar,
)

if TYPE_CHECKING:
    from typing import (
        Any,
        Optional,
        Tuple,
        Type,
    )
    
__all__: Tuple[str, ...] = (
    'Snowflakes',
)

_SnowflakeType = TypeVar(
    '_SnowflakeType',
    bound = int,
)

timestamp_bits: int = 2**64
process_id_bits: int = 2**5
thread_id_bits: int = 2**5
sequence_bits: int = 2**12
snowflake_bits: int = 2**64

class SnowflakeGenerator(Generic[_SnowflakeType]):
    if TYPE_CHECKING:
        _lock: Lock
        _closed: Event
        _epoch: datetime
        _process_id: int
        _thread_id: int
        _step: int
        _sequence: int
        _last: datetime
        
    def __init__(
        self: SnowflakeGenerator,
        epoch: datetime,
        process_id: int,
        thread_id: int,
        step: int,
        sequence: int,
        last: datetime,
    ) -> None:
        self._lock = Lock()
        self._closed = Event()
        
        if not isinstance(epoch, datetime):
            raise TypeError(f'Invalid epoch (object is not instance of datetime): {type(epoch).__name__}')

        self._epoch = epoch

        if process_id >= process_id_bits:
            raise ValueError(f'Invalid process id value (process_id value greater than {process_id_bits - 1:,}): {process_id}')

        self._process_id = process_id

        if thread_id >= thread_id_bits:
            raise ValueError(f'Invalid thread id value (thread_id value greater than {thread_id_bits - 1:,}): {thread_id}')

        self._thread_id = thread_id
        
        if step < 1:
            raise ValueError(f'Invalid step value (step value less than 1): {step}')
        
        if step >= sequence_bits:
            raise ValueError(f'Invalid step value (step value greater than {sequence_bits - 1:,})): {step}')

        self._step = step

        if sequence >= sequence_bits:
            raise ValueError(f'Invalid sequence (sequence value greater than {sequence_bits - 1:,}): {sequence}')

        self._sequence = sequence

        if last is None:
            last = datetime.now()

        if not isinstance(last, datetime):
            raise TypeError(f'Invalid last (object is not instance of datetime): {type(last).__name__}')

        self._last = last
        
    @property
    def epoch(self: SnowflakeGenerator) -> datetime:
        return self._epoch
    
    @property
    def process_id(self: SnowflakeGenerator) -> int:
        return self._process_id
    
    @property
    def thread_id(self: SnowflakeGenerator) -> int:
        return self._thread_id
    
    @property
    def step(self: SnowflakeGenerator) -> int:
        return self._step
        
    @property
    def sequence(self: SnowflakeGenerator) -> int:
        return self._sequence
    
    @sequence.setter
    def sequence(
        self: SnowflakeGenerator,
        value: int,
    ) -> None:
        if self.closed:
            raise RuntimeError(f'Cannot modify sequence value (snowflake generator is closed)')

        if value >= sequence_bits:
            raise ValueError(f'Invalid sequence (sequence value greater than {sequence_bits - 1:,}): {value}')
        
        self._sequence = value
    
    @property
    def last(self: SnowflakeGenerator) -> datetime:
        return self._last
    
    @last.setter
    def last(
        self: SnowflakeGenerator,
        value: datetime,
    ) -> None:
        if self.closed:
            raise RuntimeError(f'Cannot modify last value (snowflake generator is closed)')

        if not isinstance(value, datetime):
            raise TypeError(f'Invalid last (object is not instance of datetime): {type(value).__name__}')
        
        self._last = value

    def __iter__(self: SnowflakeGenerator) -> SnowflakeGenerator:
        return self
    
    def __next__(self: SnowflakeGenerator) -> _SnowflakeType:
        if self.closed:
            raise StopIteration('Cannot get next snowflake (snowflake generator is closed)')

        try:
            return self.generate()
        except (
            RuntimeError,
            ValueError,
        ) as e:
            raise StopIteration(f'Cannot get next snowflake ({e})')
    
    def generate(self: SnowflakeGenerator) -> _SnowflakeType:
        if self.closed:
            raise RuntimeError(f'Cannot generate snowflake (snowflake generator is closed)')

        self._lock.acquire()

        now: datetime
        sequence: int
        
        while True:
            now = datetime.now()
        
            if self.last > now:
                sleep((self.last - now).total_seconds())
                continue
        
            if self.last == now:
                sequence = (self.sequence + self.step) & (sequence_bits - 1)
            
                if sequence == 0:
                    sleep(self.step / 1000)
                    continue
            
            else:
                sequence = 0
            
            self.last = now
            self.sequence = sequence
        
            break
        
        res = (
            (int(now.timestamp() * 1000) - int(self.epoch.timestamp() * 1000)) << 22 |
            self.process_id << 17 |
            self.thread_id << 12 |
            sequence
        )
        
        self._lock.release()
        
        if res >= snowflake_bits:
            raise ValueError(f'Invalid snowflake (snowflake value greater than {snowflake_bits - 1:,}): {res}')
        
        return res
    
    def close(self: SnowflakeGenerator) -> None:
        self._closed.set()
        
    @property
    def closed(self: SnowflakeGenerator) -> bool:
        return self._closed.is_set()
