from __future__ import annotations
from datetime import datetime
from strenum import LowercaseStrEnum


class StatusPostVisibility(LowercaseStrEnum):
    """
    The visibility parameter is a string value and accepts any of: 
    
    "direct" - post will be visible only to mentioned users 
    "private" - post will be visible only to followers 
    "unlisted" - post will be public but not appear on the public timeline 
    "public" - post will be public
    """
    DIRECT = "direct"
    PRIVATE = "private"
    UNLISTED = "unlisted"
    PUBLIC = "public"

    def valid_or_raise(value: str) -> StatusPostVisibility:
        valid_items = [StatusPostVisibility.DIRECT, StatusPostVisibility.PRIVATE, StatusPostVisibility.UNLISTED, StatusPostVisibility.PUBLIC]

        if not value in valid_items:
            raise RuntimeError(f"Value [{value}] is not a valid StatusPostVisibility")
        
        return value


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
    content_type: StatusPostContentType = None
    scheduled_at: datetime = None
    poll: any = None    # Poll not supported. It should be here a Poll object
    quote_id: int = None

    def __init__(self,
                 status: str = None, 
                 in_reply_to_id: int = None, 
                 media_ids: list[int] = None,
                 sensitive: bool = False, 
                 visibility: StatusPostVisibility = StatusPostVisibility.PUBLIC, 
                 spoiler_text: str = None, 
                 language: str = None, 
                 idempotency_key: str = None, 
                 content_type: StatusPostContentType = None, 
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
            StatusPostContentType.valid_or_raise(status_post_dict["content_type"]),
            datetime.fromtimestamp(status_post_dict["scheduled_at"]),
            status_post_dict["poll"],
            status_post_dict["quote_id"],
        )


class StatusPostContentType(LowercaseStrEnum):
    """
    Specific to “pleroma” feature set:: Specify content_type to set the content type of your post on Pleroma. It accepts:

    "text/plain" (default)
    "text/markdown"
    "text/html"
    "text/bbcode"
    
    This parameter is not supported on Mastodon servers, but will be safely ignored if set.
    """

    PLAIN = "text/plain"
    MARKDOWN = "text/markdown"
    HTML = "text/html"
    BBCODE = "text/bbcode"

    def valid_or_raise(value: str) -> StatusPostContentType:
        valid_items = [StatusPostContentType.PLAIN, StatusPostContentType.MARKDOWN, StatusPostContentType.HTML, StatusPostContentType.BBCODE]

        if not value in valid_items:
            raise RuntimeError(f"Value [{value}] is not a valid StatusPostContentType")
        
        return value