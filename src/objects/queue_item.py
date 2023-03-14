from __future__ import annotations
from .message import Message
from .message_media import MessageMedia
from datetime import datetime

class QueueItem:

    message: Message
    media: list[MessageMedia]
    published_at: datetime

    def __init__(self,
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
            "media": map(lambda x: x.to_dict(), self.media) if self.media else None,
            "published_at": datetime.timestamp(self.published_at)
        }
    
    def from_dict(queue_item_dict: dict) -> QueueItem:
        return QueueItem(
            Message.from_dict(queue_item_dict["message"]),
            map(lambda x: MessageMedia.from_dict(x), queue_item_dict["media"]) if "media" in queue_item_dict and queue_item_dict["media"] else None,
            datetime.fromtimestamp(queue_item_dict["published_at"])
        )
