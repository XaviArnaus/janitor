from __future__ import annotations
from status_post_visibility import StatusPostVisibility
from content_type import ContentType
from datetime import datetime


class StatusPost:
    """
    Object to manage the status posts to be published through the Mastodon API.
    Mastodon.py wrapper version 1.8.0

    Should support Pleroma variations
    (status, in_reply_to_id=None, media_ids=None, sensitive=False, visibility=None, spoiler_text=None, language=None, idempotency_key=None, content_type=None, scheduled_at=None, poll=None, quote_id=None)
    """

    status: str = None
    in_reply_to_id: int = None
    media_ids: list[int] = None
    sensitive: bool = False
    visibility: StatusPostVisibility = StatusPostVisibility.PUBLIC
    spoiler_text: str = None
    language: str = None
    idempotency_key: str = None
    content_type: ContentType = None
    scheduled_at: datetime = None
    poll: any = None    # Poll not supported. It should be here a Poll object
    quote_id: int = None

    def __init__(self,
                 status, 
                 in_reply_to_id: int = None, 
                 media_ids: list[int] = None,
                 sensitive: bool = False, 
                 visibility: StatusPostVisibility = StatusPostVisibility.PUBLIC, 
                 spoiler_text: str = None, 
                 language: str = None, 
                 idempotency_key: str = None, 
                 content_type: ContentType = None, 
                 scheduled_at: datetime = None, 
                 poll: any = None, 
                 quote_id: int = None) -> None:
        
        self.status = status
        self.in_reply_to_id = in_reply_to_id
        self.media_ids = media_ids
        self.sensitive = sensitive
        self.visibility = visibility
        self.spoiler_text = spoiler_text
        self.language = language
        self.idempotency_key = idempotency_key
        self.content_type = content_type
        self.scheduled_at = scheduled_at
        self.poll = poll
        self.quote_id = quote_id

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "in_reply_to_id": self.in_reply_to_id,
            "media_ids": self.media_ids,
            "sensitive": self.sensitive,
            "visibility": self.visibility,
            "spoiler_text": self.spoiler_text,
            "language": self.language,
            "idempotency_key": self.idempotency_key,
            "content_type": self.content_type,
            "scheduled_at": self.scheduled_at.timestamp(),
            "poll": self.poll,
            "quote_id": self.quote_id,
        }
    
    def from_dict(status_post_dict: dict) -> StatusPost:
        return StatusPost(
            status_post_dict["status"],
            status_post_dict["in_reply_to_id"],
            status_post_dict["media_ids"],
            status_post_dict["sensitive"],
            StatusPostVisibility.valid_or_raise(status_post_dict["visibility"]),
            status_post_dict["spoiler_text"],
            status_post_dict["language"],
            status_post_dict["idempotency_key"],
            ContentType.valid_or_raise(status_post_dict["content_type"]),
            datetime.fromtimestamp(status_post_dict["scheduled_at"]),
            status_post_dict["poll"],
            status_post_dict["quote_id"],
        )