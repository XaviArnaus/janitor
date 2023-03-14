from pyxavi.config import Config
from objects.post import Post
import logging

class PostFormatter:
    """
    This class converts the object Post that we use arround in the whole application
    to the StatusPost that we use only at publishing stage.
    """

    def __init__(self, config: Config) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))

    def format(self, post: Post) -> str:
        content = ""

        if post.summary:
            content = content + post.summary

        


        return f"{}"


    def _format_post(self, post: dict, origin: str, site_options: dict) -> str:

        title = post["title"]
        title_only_chars = re.sub("^[A-Za-z]*", "", title)
        if title_only_chars == title_only_chars.upper():
            title = " ".join([word.capitalize() for word in title.lower().split(" ")])
        link = post["link"]
        summary = post["summary"] + "\n\n" if "summary" in post and post["summary"] and post["summary"] != "" else ""
        summary = ''.join(BeautifulSoup(summary, "html.parser").findAll(text=True))
        summary = summary.replace("\n\n\n", "\n\n")
        summary = re.sub("\s+", ' ', summary)
        max_length = site_options["max_summary_length"] \
            if "max_summary_length" in site_options and site_options["max_summary_length"] \
                else self.MAX_SUMMARY_LENGTH
        summary = (summary[:max_length] + '...') if len(summary) > max_length+3 else summary

        text = f"{origin}:\n" if "show_name" in site_options and site_options["show_name"] else ""
        
        return f"{text}\t{title}\n\n{summary}\n\n{link}"