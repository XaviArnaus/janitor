from __future__ import annotations
from status_post import StatusPost
from queue_item_action import QueueItemAction
from datetime import datetime

class QueueItem:

    status: StatusPost  # Used to define the StatusPost to publish
    status_id: int  # Used to define the StatusPost to reblog.
    action: QueueItemAction
    published_at: datetime

    def __init__(self,
                 status: StatusPost = None,
                 status_id: int = None,
                 action: QueueItemAction = None,
                 published_at: datetime = None
                 ) -> None:
        
        self.status = status
        self.status_id = status_id
        self.action = action
        self.published_at = published_at if published_at else datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "status": self.status.to_dict(),
            "status_id": self.status_id,
            "action": self.action,
            "published_at": datetime.timestamp(self.published_at)
        }
    
    def from_dict(queue_item_dict: dict) -> QueueItem:
        return QueueItem(
            StatusPost.from_dict(queue_item_dict["status"]),
            queue_item_dict["status_id"],
            QueueItemAction.valid_or_raise(queue_item_dict["action"]),
            datetime.fromtimestamp(queue_item_dict["published_at"])
        )
