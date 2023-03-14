from __future__ import annotations

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
    
    def from_dict(status_post_dict: dict) -> MessageMedia:
        return MessageMedia(
            status_post_dict["url"],
            status_post_dict["alt_text"],
        )