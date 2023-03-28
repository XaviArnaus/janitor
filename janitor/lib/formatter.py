from pyxavi.config import Config
from ..objects.message import Message
from janitor.objects.message import MessageType
from janitor.objects.status_post import StatusPost, StatusPostVisibility, StatusPostContentType
import logging


class Formatter:
    """
    This class converts the object Message that we use arround in the whole application
    to the StatusPost that we use only at publishing stage.
    """

    def __init__(self, config: Config) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))

    def build_status_post(self, message: Message) -> StatusPost:
        status_post = StatusPost()

        # Do we have a summary AND a text?
        #   Yes: Then we'll use the spoiler text
        #   No: Then whatever it comes becomes the status itself
        if message.summary and message.text:
            status_post.spoiler_text = self._format_spoiler(
                message.summary, message.message_type
            )
            status_post.status = self._format_status(message.text, MessageType.NONE)
        else:
            status_post.status = self._format_status(
                message.text if message.text else message.summary, message.message_type
            )

        # Now the rest of the details
        status_post.content_type = StatusPostContentType.valid_or_raise(
            value=self._config.get("status_post.content_type")
        )
        status_post.visibility = StatusPostVisibility.valid_or_raise(
            value=self._config.get("status_post.visibility")
        )

        return status_post

    def _format_spoiler(self, content: str, message_type: MessageType) -> str:
        return content

    def _format_status(self, content: str, message_type: MessageType) -> str:
        return content
