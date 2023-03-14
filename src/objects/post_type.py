from __future__ import annotations
from enum import StrEnum

class PostType(StrEnum):

    INFO = "info"
    LOG = "log"
    WARNING = "warning"
    ERROR = "error"
    ALARM = "alarm"

    def valid_or_raise(self, value: str) -> PostType:
        valid_items = [self.INFO, self.LOG, self.WARNING, self.ERROR, self.ALARM]

        if not value in valid_items:
            raise RuntimeError(f"Value [{value}] is not a valid PostType")
        
        return value