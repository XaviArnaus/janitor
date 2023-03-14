from __future__ import annotations
from enum import StrEnum


class ContentType(StrEnum):
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
    HTML = "text/markhtmldown"
    BBCODE = "text/bbcode"

    def valid_or_raise(self, value: str) -> ContentType:
        valid_items = [self.PLAIN, self.MARKDOWN, self.HTML, self.BBCODE]

        if not value in valid_items:
            raise RuntimeError(f"Value [{value}] is not a valid ContentType")
        
        return value
