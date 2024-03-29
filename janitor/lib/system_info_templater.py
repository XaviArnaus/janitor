from pyxavi.config import Config
from janitor.objects.message import Message, MessageType
from string import Template
import logging


class SystemInfoTemplater:
    """
    This class converts the system info dict to the Message object.

    It decides which template to use based on the MessageType
    """

    SUFFIXES = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    def __init__(self, config: Config) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))

    def process_report(self, system_info_data: dict) -> Message:
        thresholds = dict(self._config.get("system_info.thresholds"))
        humansize_exceptions = list(
            self._config.get("system_info.formatting.human_readable_exceptions")
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
                        thresholds[name]["message_type"] if "message_type" in
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
        template = self._get_message_template(error_level)
        return Message(
            summary=template["summary"].substitute(summary=hostname),
            text=template["text"].substitute(summary=hostname, text="\n".join(report_lines)),
            message_type=error_level
        )

    def _get_message_template(self, message_type: MessageType) -> dict:
        templates = {
            MessageType.NONE: {
                "summary": Template(
                    self._config.
                    get("system_info.formatting.templates.message_type.none.summary")
                ),
                "text": Template(
                    self._config.get("system_info.formatting.templates.message_type.none.text")
                )
            },
            MessageType.INFO: {
                "summary": Template(
                    self._config.
                    get("system_info.formatting.templates.message_type.info.summary")
                ),
                "text": Template(
                    self._config.get("system_info.formatting.templates.message_type.info.text")
                )
            },
            MessageType.WARNING: {
                "summary": Template(
                    self._config.
                    get("system_info.formatting.templates.message_type.warning.summary")
                ),
                "text": Template(
                    self._config.
                    get("system_info.formatting.templates.message_type.warning.text")
                )
            },
            MessageType.ERROR: {
                "summary": Template(
                    self._config.
                    get("system_info.formatting.templates.message_type.error.summary")
                ),
                "text": Template(
                    self._config.
                    get("system_info.formatting.templates.message_type.error.text")
                )
            },
            MessageType.ALARM: {
                "summary": Template(
                    self._config.
                    get("system_info.formatting.templates.message_type.alarm.summary")
                ),
                "text": Template(
                    self._config.
                    get("system_info.formatting.templates.message_type.alarm.text")
                )
            }
        }

        return templates[message_type]

    def _get_line_ok_template(self) -> Template:
        return Template(
            self._config.get("system_info.formatting.templates.report_lines.line_ok")
        )

    def _get_line_fail_template(self) -> Template:
        return Template(
            self._config.get("system_info.formatting.templates.report_lines.line_fail")
        )

    def _build_report_line(
        self, item_name: str, item_value: any, field_has_issue: bool = False
    ) -> str:

        title = self._config.get(
            "system_info.formatting.report_item_names_map." + item_name, item_name
        )
        self._logger.debug(f"Will receive the title [{title}]")
        template = self._get_line_ok_template()
        if field_has_issue:
            template = self._get_line_fail_template()
        return template.substitute(title=title, value=item_value)

    def _humansize(self, nbytes):
        """
        Based on https://stackoverflow.com/questions/14996453/python-libraries-to-calculate-human-readable-filesize-from-bytes # noqa: E501
        """

        if not self._config.get("system_info.formatting.human_readable", False):
            return f"{nbytes} {self.SUFFIXES[0]}"

        i = 0
        while nbytes >= 1024 and i < len(self.SUFFIXES) - 1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, self.SUFFIXES[i])
