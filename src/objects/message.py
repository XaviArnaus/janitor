from __future__ import annotations
from .message_type import MessageType

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
    
    def from_dict(status_post_dict: dict) -> Message:
        print(status_post_dict)
        return Message(
            status_post_dict["summary"],
            status_post_dict["text"],
            MessageType.valid_or_raise(value = status_post_dict["type"]),
        )