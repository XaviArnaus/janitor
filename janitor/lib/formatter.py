from pyxavi.config import Config
from ..objects.message import Message
from janitor.objects.message import MessageType
from janitor.objects.status_post import StatusPost, StatusPostVisibility, StatusPostContentType
from string import Template
import logging


class Formatter:
    """
    This class converts the object Message that we use arround in the whole application
    to the StatusPost that we use only at publishing stage.
    """

    TEMPLATE_TEXT_WITH_MENTION = "$mention:\n\n$text"

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
            value=self._config.get("mastodon.status_post.content_type")
        )
        status_post.visibility = StatusPostVisibility.valid_or_raise(
            value=self._config.get("mastodon.status_post.visibility")
        )

        # We always have to have a status (main text).
        # So we apply here the mention in case it's a direct message
        status_post.status = self.add_mention_to_message_if_direct_visibility(status_post.status)

        return status_post

    def _format_spoiler(self, content: str, message_type: MessageType) -> str:
        return content

    def _format_status(self, content: str, message_type: MessageType) -> str:
        return content
    
    def add_mention_to_message_if_direct_visibility(self, text: str) -> str:
        is_dm = self._config.get("mastodon.status_post.visibility") == StatusPostVisibility.DIRECT
        mention = self._config.get("mastodon.status_post.username_to_dm")

        if is_dm and mention:
            self._logger.info(f"It's a DM posting, applying mention to {mention}")
            return Template(self.TEMPLATE_TEXT_WITH_MENTION).substitute(
                mention=mention,
                text=text
            )
        else:
            if is_dm and not mention:
                self._logger.error(f"It's a DM posting, but there is no mention! \
                                   Make sure the config has the parameter \
                                   [mastodon.status_post.username_to_dm]. \
                                   The post won't be actually visible to anybody!")
            else:
                self._logger.debug("Not a DM posting, not adding a mention")
            
            return text

