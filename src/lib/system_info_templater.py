from pyxavi.config import Config
from objects.message import Message
from objects.message_type import MessageType
from string import Template
import logging

class SystemInfoTemplater:
    """
    This class converts the system info dict to the Message object.

    It also decides if the message should be an alarm based on the thresholds in the config
    """

    TEMPLATES = {
        MessageType.NONE: {
            "summary": None,
            "text": Template("$text")
        },
        MessageType.INFO: {
            "summary": Template("ℹ️ $summary"),
            "text": Template("$text")
        },
        MessageType.WARNING: {
            "summary": Template("⚠️ $summary"),
            "text": Template("$text")
        },
        MessageType.ERROR: {
            "summary": Template("🔥 $summary"),
            "text": Template("$text")
        },
        MessageType.ALARM: {
            "summary": Template("🚨 $summary"),
            "text": Template("$text")
        }
    }

    def __init__(self, config: Config) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))

    def build_message(self, system_info_data: dict) -> Message:
        thresholds = self._config.get("system_info.thresholds")
        pass

    def _humansize(self, nbytes):
        """
        Based on https://stackoverflow.com/questions/14996453/python-libraries-to-calculate-human-readable-filesize-from-bytes
        """

        if not self._config.get("system_info.human_readable", False):
            return f"{nbytes} {self.SUFFIXES[0]}"

        i = 0
        while nbytes >= 1024 and i < len(self.SUFFIXES)-1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, self.SUFFIXES[i])


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