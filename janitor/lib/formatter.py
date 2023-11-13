from pyxavi.terminal_color import TerminalColor
from pyxavi.config import Config
from ..objects.message import Message
from janitor.objects.message import MessageType
from janitor.objects.status_post import StatusPost, StatusPostVisibility
from janitor.objects.mastodon_connection_params import MastodonStatusParams
from string import Template
import logging


class Formatter:
    """
    This class converts the object Message that we use arround in the whole application
    to the StatusPost that we use only at publishing stage.
    """

    def __init__(self, config: Config, status_params: MastodonStatusParams) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))
        self._status_params = status_params
        self._merge_summary_into_text = config.get("formatter.merge_summary_into_text", False)
        self._templates = {
            "merge_strategies": {
                "text_with_mention": config.get(
                    "formatter.templates.merge_strategies.mention_into_text",
                    "$text\n\n$mention"
                ),
                "summary_into_text": config.get(
                    "formatter.templates.merge_strategies.summary_into_text",
                    "$summary\n\n$text"
                ),
            },
            MessageType.NONE: {
                "summary": config.get(
                    "formatter.templates.message_type.none.summary", "$summary"
                ),
                "text": config.get("formatter.templates.message_type.none.text", "$text")
            },
            MessageType.INFO: {
                "summary": config.get(
                    "formatter.templates.message_type.info.summary", "$summary"
                ),
                "text": config.get("formatter.templates.message_type.info.text", "$text")
            },
            MessageType.WARNING: {
                "summary": config.get(
                    "formatter.templates.message_type.warning.summary", "$summary"
                ),
                "text": config.get("formatter.templates.message_type.warning.text", "$text")
            },
            MessageType.ERROR: {
                "summary": config.get(
                    "formatter.templates.message_type.error.summary", "$summary"
                ),
                "text": config.get("formatter.templates.message_type.error.text", "$text")
            },
            MessageType.ALARM: {
                "summary": config.get(
                    "formatter.templates.message_type.alarm.summary", "$summary"
                ),
                "text": config.get("formatter.templates.message_type.alarm.text", "$text")
            }
        }

    def build_status_post(self, message: Message) -> StatusPost:
        status_post = StatusPost()

        # Do we have a summary AND a text?
        #   Yes: Then we'll use the spoiler text
        #   No: Then whatever it comes becomes the status itself
        if message.summary and message.text:
            status_post.spoiler_text = self._format_spoiler(message)
        status_post.status = self._format_status(message)

        # Now the rest of the details
        status_post.content_type = self._status_params.content_type
        status_post.visibility = self._status_params.visibility

        # We always have to have a status (main text).
        # So we apply here the mention in case it's a direct message
        status_post.status = self.add_mention_to_message_if_direct_visibility(
            status_post.status
        )

        return status_post

    def _format_spoiler(self, message: Message) -> str:
        content = Template(self._templates[message.message_type]["summary"]
                           ).substitute(summary=message.summary)
        return content

    def _format_status(self, message: Message) -> str:
        # Can happen that we receive only the summary, then we use it as text
        content = Template(self._templates[message.message_type]["text"]
                           ).substitute(text=message.text if message.text else message.summary)

        # Following up, even we are meant to merge summary and text,
        #   if there is no text we just ignore, as we already used summary as text.
        if self._merge_summary_into_text and message.summary and message.text:
            summary = self._format_spoiler(message=message)
            content = Template(self._templates["merge_strategies"]["summary_into_text"])\
                .substitute(
                    summary=summary,
                    text=content
                )
        return content

    def add_mention_to_message_if_direct_visibility(self, text: str) -> str:
        is_dm = self._status_params.visibility in [
            StatusPostVisibility.PRIVATE, StatusPostVisibility.DIRECT
        ]
        mention = self._status_params.username_to_dm

        if is_dm and mention:
            self._logger.debug(f"It's a DM posting, applying mention to {mention}")
            return Template(self._templates["merge_strategies"]["text_with_mention"])\
                .substitute(mention=mention, text=text)
        else:
            if is_dm and not mention:
                self._logger.error(
                    f"{TerminalColor.RED_BRIGHT}It's a DM posting, but there is no user mention! \
                    Make sure the named_account has the parameter \
                    [username_to_dm]. \
                    The post won't be actually visible to anybody!{TerminalColor.END}"
                )
            else:
                self._logger.debug("Not a DM posting, not adding a mention")

            return text
