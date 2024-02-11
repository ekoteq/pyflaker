from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple
    
__all__: Tuple[str, ...] = (
    "Snowflake",
)

class Snowflake:
    if TYPE_CHECKING:
        epoch: datetime
        time: timedelta
        salt: int
        sequence: int
        
    __slots__: Tuple[str, ...] = (
        "epoch",
        "time",
        "salt",
        "sequence",
    )

    def __init__(
        self: Snowflake,
        epoch: datetime,
        time: timedelta,
        salt: int,
        sequence: int,
    ):
        self.epoch = epoch
        self.time = time
        self.salt = salt
        self.sequence = sequence

    def __int__(self: Snowflake) -> int:
        return (
            (int(self.time.total_seconds() * 1000) << 22) |
            (self.salt << 12) |
            self.sequence
        )

    def __repr__(self: Snowflake) -> str:
        return (
            "<"
            f"{self.__class__.__name__}"
            f" epoch = {self.epoch!r}"
            f", time = {self.time!r}"
            f", salt = {self.salt!r}"
            f", sequence = {self.sequence!r}"
            " >"
        )

    def __str__(self: Snowflake) -> str:
        return str(int(self))

    def __hash__(self: Snowflake) -> int:
        return hash(int(self)) 

    def __bytes__(self: Snowflake) -> bytes:
        return int(self).to_bytes(8, "big")
    
    def __bool__(self: Snowflake) -> bool:
        return not int(self) == 0
    
    def __sizeof__(self: Snowflake) -> int:
        return int(self).__sizeof__()
