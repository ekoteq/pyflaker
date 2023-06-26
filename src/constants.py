from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from typing import Tuple

__all__: Tuple[str, ...] = (
    'EKO_EPOCH',
    'EKO_EPOCH_TIMESTAMP_MS',
    'EKO_EPOCH_TIMESTAMP_S',
)

# this value is stored like this so the
# date is human readable and easily updateable
EKO_EPOCH: datetime = datetime.timestamp(datetime(
    year = 2019,
    month = 4,
    day = 13,
    hour = 4,
    minute = 12,
))

EKO_EPOCH_TIMESTAMP_MS: int = int(EKO_EPOCH * 1000)
EKO_EPOCH_TIMESTAMP_S: int = int(EKO_EPOCH)
