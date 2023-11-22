from __future__ import annotations
from pyxavi.item_queue import QueueItemProtocol
from .message import Message, MessageMedia
from datetime import datetime


class QueueItem(QueueItemProtocol):

    message: Message
    media: list[MessageMedia]
    published_at: datetime

    def __init__(
        self,
        message: Message = None,
        media: list[MessageMedia] = None,
        published_at: datetime = None
    ) -> None:

        self.message = message
        self.media = media
        self.published_at = published_at if published_at else datetime.now()

    def to_dict(self) -> dict:
        return {
            "message": self.message.to_dict(),
            "media": list(map(lambda x: x.to_dict(), self.media)) if self.media else None,
            "published_at": datetime.timestamp(self.published_at)
        }

    @staticmethod
    def from_dict(queue_item_dict: dict) -> QueueItem:
        return QueueItem(
            Message.from_dict(queue_item_dict["message"])
            if "message" in queue_item_dict else None,
            list(map(lambda x: MessageMedia.from_dict(x), queue_item_dict["media"]))
            if "media" in queue_item_dict and queue_item_dict["media"] else None,
            datetime.fromtimestamp(queue_item_dict["published_at"])
            if "published_at" in queue_item_dict else None
        )
    
    def sort_value(self, param: any = None) -> any:
        return self.published_at
    
    def unique_value(self, param: any = None) -> any:
        result = f"s{self.message.summary}" if self.message.summary is not None else ""
        result += f"m{self.message.text}" if self.message.text is not None else ""
        return result
