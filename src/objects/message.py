from __future__ import annotations
from strenum import LowercaseStrEnum


class Message:

    summary: str = None
    text: str = None
    type: MessageType = None

    def __init__(self,
                 summary: str = None,
                 text: str = None,
                 type: MessageType = None,
                 ) -> None:

        self.summary = summary
        self.text = text
        self.type = type if type else MessageType.NONE

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "text": self.text,
            "type": str(self.type),
        }
    
    def from_dict(message_dict: dict) -> Message:
        return Message(
            summary = message_dict["summary"] if "summary" in message_dict else None,
            text = message_dict["text"] if "text" in message_dict else None,
            type = MessageType.valid_or_raise(value = message_dict["type"]) if "type" in message_dict else None,
        )


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


class MessageMedia:

    url: str = None
    alt_text: str = None

    def __init__(self,
                 url: str = None,
                 alt_text: str = None,
                 ) -> None:

        self.url = url
        self.alt_text = alt_text

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "alt_text": self.alt_text,
        }
    
    def from_dict(message_media_dict: dict) -> MessageMedia:
        return MessageMedia(
            message_media_dict["url"] if "url" in message_media_dict else None,
            message_media_dict["alt_text"] if "alt_text" in message_media_dict else None,
        )