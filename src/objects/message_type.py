from __future__ import annotations
from strenum import LowercaseStrEnum

class MessageType(LowercaseStrEnum):

    NONE = "none"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    ALARM = "alarm"

    def valid_or_raise(value: str) -> MessageType:
        valid_items = list(map(lambda x: str(x), MessageType.priority()))

        if not value in valid_items:
            raise RuntimeError(f"Value [{value}] is not a valid MessageType")
        
        return value
    
    def priority() -> list:
        return [MessageType.NONE, MessageType.INFO, MessageType.WARNING, MessageType.ERROR, MessageType.ALARM]
    
    def icon_per_type(message_type: MessageType) -> str:
        icon_per_type = {
            MessageType.NONE: "",
            MessageType.INFO: "ℹ️",
            MessageType.WARNING: "⚠️",
            MessageType.ERROR: "🔥",
            MessageType.ALARM: "🚨"
        }
        return icon_per_type[message_type]