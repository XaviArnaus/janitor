from __future__ import annotations
from enum import StrEnum


class StatusPostVisibility(StrEnum):
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

    def valid_or_raise(self, value: str) -> StatusPostVisibility:
        valid_items = [self.DIRECT, self.PRIVATE, self.UNLISTED, self.PUBLIC]

        if not value in valid_items:
            raise RuntimeError(f"Value [{value}] is not a valid StatusPostVisibility")
        
        return value
