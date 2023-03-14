from __future__ import annotations
from enum import StrEnum

class QueueItemAction(StrEnum):

    NEW = "new"
    REBLOG = "reblog"

    def valid_or_raise(self, value: str) -> QueueItemAction:
        valid_items = [self.NEW, self.REBLOG]

        if not value in valid_items:
            raise RuntimeError(f"Value [{value}] is not a valid QueueItemAction")
        
        return value