from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from typing import Tuple, Optional

__all__: Tuple[str, ...] = (
    'EKO_EPOCH',
    'EKO_EPOCH_TIMESTAMP_MS',
    'EKO_EPOCH_TIMESTAMP_S',
)

def now(tz: Optional[timezone]) -> datetime:
    return datetime.now(tz = tz)

def timestamp(dt: Optional[datetime] = None) -> int:
    if dt is None:
        dt = now()

    return int(dt.timestamp() * 1000)
