from pyxavi.config import Config
from janitor.objects.message import Message, MessageType
from string import Template
import logging


class SystemInfoTemplater:
    """
    This class converts the system info dict to the Message object.

    It decides which template to use based on the MessageType
    """

    MESSAGE_TEMPLATE = {
        MessageType.NONE: {
            "summary": None, "text": Template("$text")
        },
        MessageType.INFO: {
            "summary": Template("ℹ️ $summary"), "text": Template("$text")
        },
        MessageType.WARNING: {
            "summary": Template("⚠️ $summary"), "text": Template("$text")
        },
        MessageType.ERROR: {
            "summary": Template("🔥 $summary"), "text": Template("$text")
        },
        MessageType.ALARM: {
            "summary": Template("🚨 $summary"), "text": Template("$text")
        }
    }
    REPORT_LINE_TEMPLATE_OK = Template("- **$title**: $value")
    REPORT_LINE_TEMPLATE_ISSUE = Template("- **$title**: $value ❗️")
    SUFFIXES = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    def __init__(self, config: Config) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))

    def process_report(self, system_info_data: dict) -> Message:
        thresholds = dict(self._config.get("system_info.thresholds"))
        humansize_exceptions = list(
            self._config.get("formatting.system_info.human_readable_exceptions")
        )
        hostname = system_info_data.pop("hostname") if "hostname" in system_info_data\
            else "unknown host"

        report_lines = []
        error_type = []
        for name, value in system_info_data.items():
            field_has_issue = False
            self._logger.debug(f"Processing [{name}]")
            # Check if we're monitoring this metric and if the condition applies
            if name in thresholds.keys():
                if "value" in thresholds[name] and value > thresholds[name]["value"]:
                    self._logger.debug(f"The metric [{name}] is greater than the threshold")
                    error_type.append(
                        thresholds[name]["type"] if "type" in
                        thresholds[name] else MessageType.WARNING
                    )
                    field_has_issue = True
            # Create the string that will display the line
            report_lines.append(
                self._build_report_line(
                    name,
                    value if name in humansize_exceptions else self._humansize(value),
                    field_has_issue
                )
            )

        # Crunch errors to the highest
        if (error_type):
            error_type = list(map(lambda x: MessageType.priority().index(x), error_type))
            error_level = MessageType.priority()[max(error_type)]
        else:
            error_level = MessageType.INFO

        # Apply the template related to the MessageType
        template = self.MESSAGE_TEMPLATE[error_level]
        return Message(
            summary=template["summary"].substitute(summary=hostname),
            text=template["text"].substitute(text="\n".join(report_lines)),
            message_type=error_level
        )

    def _build_report_line(
        self, item_name: str, item_value: any, field_has_issue: bool = False
    ) -> str:

        title = self._config.get(
            "formatting.system_info.report_item_names_map." + item_name, item_name
        )
        self._logger.debug(f"Will receive the title [{title}]")
        template = self.REPORT_LINE_TEMPLATE_OK
        if field_has_issue:
            template = self.REPORT_LINE_TEMPLATE_ISSUE
        return template.substitute(title=title, value=item_value)

    def _humansize(self, nbytes):
        """
        Based on https://stackoverflow.com/questions/14996453/python-libraries-to-calculate-human-readable-filesize-from-bytes # noqa: E501
        """

        if not self._config.get("formatting.system_info.human_readable", False):
            return f"{nbytes} {self.SUFFIXES[0]}"

        i = 0
        while nbytes >= 1024 and i < len(self.SUFFIXES) - 1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, self.SUFFIXES[i])
