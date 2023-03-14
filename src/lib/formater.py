from pyxavi.config import Config
from objects.message import Message
from objects.message_type import MessageType
from objects.status_post import StatusPost
from objects.status_post_visibility import StatusPostVisibility
from objects.status_post_content_type import StatusPostContentType
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
            status_post.spoiler_text = self._format_spoiler(message.summary, message.type)
            status_post.status = self._format_status(message.text, MessageType.NONE)
        else:
            status_post.status = self._format_status(message.text if message.text else message.summary, message.type)
        
        # Now the rest of the details
        status_post.content_type = StatusPostContentType.valid_or_raise(self._config.get("status_post.content_type"))
        status_post.visibility = StatusPostVisibility.valid_or_raise(self._config.get("status_post.visibility"))

        return status_post
    
    def _format_spoiler(self, content: str, message_type: MessageType) -> str:
        return content
    
    def _format_status(self, content: str, message_type: MessageType) -> str:
        return content


    # def _format_post(self, post: dict, origin: str, site_options: dict) -> str:

    #     title = post["title"]
    #     title_only_chars = re.sub("^[A-Za-z]*", "", title)
    #     if title_only_chars == title_only_chars.upper():
    #         title = " ".join([word.capitalize() for word in title.lower().split(" ")])
    #     link = post["link"]
    #     summary = post["summary"] + "\n\n" if "summary" in post and post["summary"] and post["summary"] != "" else ""
    #     summary = ''.join(BeautifulSoup(summary, "html.parser").findAll(text=True))
    #     summary = summary.replace("\n\n\n", "\n\n")
    #     summary = re.sub("\s+", ' ', summary)
    #     max_length = site_options["max_summary_length"] \
    #         if "max_summary_length" in site_options and site_options["max_summary_length"] \
    #             else self.MAX_SUMMARY_LENGTH
    #     summary = (summary[:max_length] + '...') if len(summary) > max_length+3 else summary

    #     text = f"{origin}:\n" if "show_name" in site_options and site_options["show_name"] else ""
        
    #     return f"{text}\t{title}\n\n{summary}\n\n{link}"