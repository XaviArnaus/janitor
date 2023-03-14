from __future__ import annotations
from enum import StrEnum

class MessageType(StrEnum):

    NONE = "none"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    ALARM = "alarm"

    def valid_or_raise(self, value: str) -> MessageType:
        valid_items = [self.NONE, self.INFO, self.WARNING, self.ERROR, self.ALARM]

        if not value in valid_items:
            raise RuntimeError(f"Value [{value}] is not a valid MessageType")
        
        return value