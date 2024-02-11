from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
)
from threading import Lock
from time import sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import (
        Optional,
        Tuple,
    )
    
__all__: Tuple[str, ...] = (
    "SnowflakeGenerator",
)

class SnowflakeGenerator:
    if TYPE_CHECKING:
        lock: Lock
        epoch: datetime
        salt: int
        sequence: int
        last_time: datetime
        
    __slots__: Tuple[str, ...] = (
        "lock",
        "epoch",
        "salt",
        "sequence",
        "last_time",
    )

    def __init__(
        self,
        epoch: datetime,
        salt: Optional[int] = 0,
        sequence: Optional[int] = 0,
    ):
        self.lock = Lock()

        self.epoch = epoch
        self.salt = salt
        self.sequence = sequence
        self.last_time = self.epoch

    def generate(self) -> int:
        with self.lock:
            while True:
                now: datetime = datetime.utcnow()

                # check if time is going backwards
                if now < self.last_time:
                    # wait until time catches up
                    sleep((self.last_time - now).total_seconds())
                    continue

                if now == self.last_time:
                    # don't update instance attribute in case of overflow
                    sequence = (self.sequence + 1) & ((1 << 2**10) - 1) # 2**10 = 1024, 10 bits

                    # check for overflow
                    if self.sequence == 0:
                        # Wait 1 millisecond if sequence overflows
                        sleep(1/1000)
                        continue
                    
                    # only update instance attribute if there's no overflow
                    self.sequence = sequence
                else:
                    self.sequence = 0

                self.last_time = now
                break

            # construct while locked so sequence and time won't change
            snowflake: Snowflake = Snowflake(
                epoch = self.epoch,
                time = timedelta(milliseconds = (self.last_time - self.epoch).total_seconds()),
                salt = self.salt,
                sequence = self.sequence,
            )

            return snowflake
