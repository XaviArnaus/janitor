from pyxavi.config import Config
from janitor.objects.message import Message, MessageType
from janitor.lib.system_info_templater import SystemInfoTemplater
from unittest.mock import patch, Mock
from string import Template
import pytest
from logging import Logger

CONFIG = {
    "logger.name": "logger_test",
    "system_info.thresholds": {
        "cpu_percent": {
            "value": 80.0, "type": "warning"
        },
        "memory_percent": {
            "value": 80.0, "type": "warning"
        },
        "disk_usage_percent": {
            "value": 80.0, "type": "alarm"
        },
    },
    "system_info.formatting.human_readable_exceptions": [
        "cpu_percent", "cpu_count", "memory_percent", "disk_usage_percent"
    ],
    "system_info.formatting.templates.message_type.none.summary": "⚠️ $summary",
    "system_info.formatting.templates.message_type.none.text": "$text",
    "system_info.formatting.templates.message_type.info.summary": "⚠️ $summary",
    "system_info.formatting.templates.message_type.info.text": "$text",
    "system_info.formatting.templates.message_type.warning.summary": "⚠️ $summary",
    "system_info.formatting.templates.message_type.warning.text": "$text",
    "system_info.formatting.templates.message_type.error.summary": "⚠️ $summary",
    "system_info.formatting.templates.message_type.error.text": "$text",
    "system_info.formatting.templates.message_type.alarm.summary": "⚠️ $summary",
    "system_info.formatting.templates.message_type.alarm.text": "$text",
}


def patched_config_init(self):
    pass


def patched_config_get(self, param: str, default=None) -> str:
    return CONFIG[param]


def get_instance() -> SystemInfoTemplater:
    with patch.object(Config, "__init__", new=patched_config_init):
        with patch.object(Config, "get", new=patched_config_get):
            return SystemInfoTemplater(config=Config())


def test_initialize():
    templater = get_instance()

    assert isinstance(templater, SystemInfoTemplater)
    assert isinstance(templater._config, Config)
    assert isinstance(templater._logger, Logger)


def test_build_report_line_no_issue():
    item_name = "metric_name"
    title_item_name = "Title for the metric name"
    item_value = 45
    field_has_issue = False
    line_template = "- **$title**: $value"

    templater = get_instance()

    mocked_config_get = Mock()
    mocked_config_get.side_effect = [title_item_name, line_template]
    with patch.object(Config, "get", new=mocked_config_get):
        templated_line = templater._build_report_line(
            item_name=item_name, item_value=item_value, field_has_issue=field_has_issue
        )

    expected_string = Template(line_template).substitute(
        title=title_item_name, value=item_value
    )

    assert templated_line == expected_string


def test_build_report_line_with_issue():
    item_name = "metric_name"
    title_item_name = "Title for the metric name"
    item_value = 45
    field_has_issue = True
    line_template = "- **$title**: $value"
    line_template_fail = "- **$title**: $value ❗️"

    templater = get_instance()

    mocked_config_get = Mock()
    mocked_config_get.side_effect = [title_item_name, line_template, line_template_fail]
    with patch.object(Config, "get", new=mocked_config_get):
        templated_line = templater._build_report_line(
            item_name=item_name, item_value=item_value, field_has_issue=field_has_issue
        )

    expected_string = Template(line_template_fail).substitute(
        title=title_item_name, value=item_value
    )

    assert templated_line == expected_string


@pytest.mark.parametrize(
    argnames=('value', 'expected_result'),
    argvalues=[
        (123, "123 B"),
        (1023, "1023 B"),
        (1024, "1 KB"),
        (1048575, "1024 KB"),
        (1048576, "1 MB"),
        (1073741823, "1024 MB"),
        (1073741824, "1 GB"),
        (1099511627775, "1024 GB"),
        (1099511627776, "1 TB"),
    ],
)
def test_humansize(value, expected_result):
    templater = get_instance()

    mocked_readable = Mock()
    mocked_readable.return_value = True
    with patch.object(Config, "get", new=mocked_readable):
        result = templater._humansize(value)

    print(result)
    assert result == expected_result


@pytest.mark.parametrize(
    argnames=('value', 'expected_result'),
    argvalues=[
        (123, "123 B"),
        (1023, "1023 B"),
        (1024, "1024 B"),
        (1048575, "1048575 B"),
        (1048576, "1048576 B"),
        (1073741823, "1073741823 B"),
        (1073741824, "1073741824 B"),
        (1099511627775, "1099511627775 B"),
        (1099511627776, "1099511627776 B"),
    ],
)
def test_humansize_no(value, expected_result):
    templater = get_instance()

    mocked_readable = Mock()
    mocked_readable.return_value = False
    with patch.object(Config, "get", new=mocked_readable):
        result = templater._humansize(value)

    print(result)
    assert result == expected_result


def test_process_report():
    hostname = "endor"
    data = {
        "hostname": hostname,
        "cpu_percent": 50,
        "cpu_count": 4,
        "memory_free": 2000,
        "memory_percent": 85,
    }
    template_ok = Template("ok $value")
    template_ko = Template("ko $value")

    templater = get_instance()

    mocked_config_get = Mock()
    # The first call to "get" returns the thresholds
    # and the second the exceptions
    mocked_config_get.side_effect = [
        CONFIG["system_info.thresholds"],
        CONFIG["system_info.formatting.human_readable_exceptions"],
        CONFIG["system_info.formatting.templates.message_type.none.summary"],
        CONFIG["system_info.formatting.templates.message_type.none.text"],
        CONFIG["system_info.formatting.templates.message_type.info.summary"],
        CONFIG["system_info.formatting.templates.message_type.info.text"],
        CONFIG["system_info.formatting.templates.message_type.warning.summary"],
        CONFIG["system_info.formatting.templates.message_type.warning.text"],
        CONFIG["system_info.formatting.templates.message_type.error.summary"],
        CONFIG["system_info.formatting.templates.message_type.error.text"],
        CONFIG["system_info.formatting.templates.message_type.alarm.summary"],
        CONFIG["system_info.formatting.templates.message_type.alarm.text"],
    ]
    mocked_build_line = Mock()
    mocked_build_line.side_effect = [
        template_ok.substitute(value=50),
        template_ok.substitute(value=4),
        template_ok.substitute(value="2 MB"),
        template_ko.substitute(value=85),
    ]
    mocked_humansize = Mock()
    mocked_humansize.return_value = "2 MB"
    with patch.object(Config, "get", new=mocked_config_get):
        with patch.object(templater, "_build_report_line", new=mocked_build_line):
            with patch.object(templater, "_humansize", new=mocked_humansize):
                content = templater.process_report(data)

    expected_content = Message(
        summary="⚠️ " + hostname,
        text="\n".join(
            [
                template_ok.substitute(value=50),
                template_ok.substitute(value=4),
                template_ok.substitute(value="2 MB"),
                template_ko.substitute(value=85),
            ]
        ),
        message_type=MessageType.WARNING
    )

    assert content.summary == expected_content.summary
    assert content.text == expected_content.text
    assert content.message_type == expected_content.message_type
