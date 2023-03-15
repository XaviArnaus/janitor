from __future__ import annotations
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
