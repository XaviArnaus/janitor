from pyxavi.config import Config
from pyxavi.logger import Logger
from janitor.lib.system_info import SystemInfo
from janitor.lib.system_info_templater import SystemInfoTemplater
from janitor.lib.publisher import Publisher
from janitor.objects.message import Message, MessageType
from janitor.runners.listen import ListenMessage, ListenSysInfo
from unittest.mock import patch, Mock, call
import pytest
from logging import Logger as PythonLogger
from flask_restful import reqparse

COLLECTED_DATA = {
    "hostname": "endor",
    "cpu": {
        "cpu_percent": 50,
        "cpu_count": 2,
    },
    "memory": {
        "memory_total": 8000,
        "memory_avail": 4000,
        "memory_used": 3000,
        "memory_free": 2000,
        "memory_percent": 40,
    },
    "disk": {
        "disk_usage_total": 8000,
        "disk_usage_used": 4000,
        "disk_usage_free": 2000,
        "disk_usage_percent": 20
    }
}

CONFIG_MASTODON_CONN_PARAMS = {
    "app_type": "SuperApp",
    "instance_type": "mastodon",
    "api_base_url": "https://mastodont.cat",
    "credentials": {
        "user_file": "user.secret",
        "client_file": "client.secret",
        "user": {
            "email": "bot+syscheck@my-fancy.site",
            "password": "SuperSecureP4ss",
        }
    }
}

ICONS = {
    MessageType.NONE: "",
    MessageType.INFO: "1",
    MessageType.WARNING: "2",
    MessageType.ERROR: "3",
    MessageType.ALARM: "4"
}


def patched_get_hostname(self):
    return COLLECTED_DATA["hostname"]


def patched_get_cpu_data(self):
    return COLLECTED_DATA["cpu"]


def patched_get_mem_data(self):
    return COLLECTED_DATA["memory"]


def patched_get_disk_data(self):
    return COLLECTED_DATA["disk"]


@pytest.fixture
def collected_data():
    return {
        **{
            "hostname": COLLECTED_DATA["hostname"]
        },
        **COLLECTED_DATA["cpu"],
        **COLLECTED_DATA["memory"],
        **COLLECTED_DATA["disk"]
    }


def patched_generic_init(self):
    pass


def patched_generic_init_with_config(self, config):
    pass


def patched_config_get(self, param):
    if param == "mastodon.named_accounts.default":
        return CONFIG_MASTODON_CONN_PARAMS


def patched_publisher_init(self, config, connection_params, base_path):
    pass


def patched_parser_add_argument(self, *args, **kwargs):
    pass


@patch.object(reqparse.RequestParser, "__init__", new=patched_generic_init)
@patch.object(Config, "__init__", new=patched_generic_init)
@patch.object(Logger, "__init__", new=patched_generic_init_with_config)
@patch.object(SystemInfo, "__init__", new=patched_generic_init_with_config)
def get_instance_sys_info() -> ListenSysInfo:
    mocked_official_logger = Mock()
    mocked_official_logger.__class__ = PythonLogger
    mocked_logger_get_logger = Mock()
    mocked_logger_get_logger.return_value = mocked_official_logger
    with patch.object(Logger, "get_logger", new=mocked_logger_get_logger):
        return ListenSysInfo(config=Config(), logger=mocked_official_logger)


def test_init_sys_info():
    mocked_reqparser_add_argument = Mock()
    with patch.object(reqparse.RequestParser, "add_argument",
                      new=mocked_reqparser_add_argument):
        runner = get_instance_sys_info()

    assert isinstance(runner, ListenSysInfo)
    assert isinstance(runner._config, Config)
    assert isinstance(runner._logger, PythonLogger)
    assert isinstance(runner._sys_info, SystemInfo)
    mocked_reqparser_add_argument.assert_called_once_with(
        'sys_data', type=dict, required=True, help='No sys_data provided', location='json'
    )


@patch.object(reqparse.RequestParser, "add_argument", new=patched_parser_add_argument)
def test_post_data_does_not_come_in_post():

    listener = get_instance_sys_info()

    mocked_parse_args = Mock()
    mocked_parse_args.return_value = {"not_wanted": "parameter"}
    with patch.object(listener._parser, "parse_args", new=mocked_parse_args):
        result, code = listener.post()

    mocked_parse_args.assert_called_once()
    assert result == {"error": "Expected dict under a \"sys_data\" variable was not present."}
    assert code == 400


@patch.object(reqparse.RequestParser, "add_argument", new=patched_parser_add_argument)
def test_post_data_comes_in_post_no_crossed_thresholds(collected_data):

    listener = get_instance_sys_info()

    mocked_parse_args = Mock()
    mocked_parse_args.return_value = {"sys_data": collected_data}
    mocked_crossed_thresholds = Mock()
    mocked_crossed_thresholds.return_value = False
    with patch.object(listener._parser, "parse_args", new=mocked_parse_args):
        with patch.object(SystemInfo, "crossed_thresholds", new=mocked_crossed_thresholds):
            code = listener.post()

    mocked_parse_args.assert_called_once()
    mocked_crossed_thresholds.assert_called_once_with(collected_data, ["hostname"])
    assert code == 200


@patch.object(reqparse.RequestParser, "add_argument", new=patched_parser_add_argument)
@patch.object(SystemInfoTemplater, "__init__", new=patched_generic_init_with_config)
@patch.object(Config, "get", new=patched_config_get)
@patch.object(Publisher, "__init__", new=patched_publisher_init)
def test_post_data_comes_in_post_crossed_thresholds(collected_data):
    message = Message(text="content of the report")

    listener = get_instance_sys_info()

    mocked_parse_args = Mock()
    mocked_parse_args.return_value = {"sys_data": collected_data}
    mocked_crossed_thresholds = Mock()
    mocked_crossed_thresholds.return_value = True
    mocked_templater_process_report = Mock()
    mocked_templater_process_report.return_value = message
    mocked_publisher_publish_message = Mock()
    with patch.object(listener._parser, "parse_args", new=mocked_parse_args):
        with patch.object(SystemInfo, "crossed_thresholds", new=mocked_crossed_thresholds):
            with patch.object(SystemInfoTemplater,
                              "process_report",
                              new=mocked_templater_process_report):
                with patch.object(Publisher,
                                  "publish_message",
                                  new=mocked_publisher_publish_message):
                    code = listener.post()

    mocked_parse_args.assert_called_once()
    mocked_crossed_thresholds.assert_called_once_with(collected_data, ["hostname"])
    mocked_templater_process_report.assert_called_once_with(collected_data)
    # For any reason I can't ensure that publish_queue_item()
    #   is called with the mocked queue item!
    mocked_publisher_publish_message.assert_called_once()
    assert code == 200


@patch.object(reqparse.RequestParser, "__init__", new=patched_generic_init)
@patch.object(Config, "__init__", new=patched_generic_init)
@patch.object(Logger, "__init__", new=patched_generic_init_with_config)
def get_instance_message() -> ListenMessage:
    mocked_official_logger = Mock()
    mocked_official_logger.__class__ = PythonLogger
    mocked_logger_get_logger = Mock()
    mocked_logger_get_logger.return_value = mocked_official_logger
    with patch.object(Logger, "get_logger", new=mocked_logger_get_logger):
        return ListenMessage(config=Config(), logger=mocked_official_logger)


def test_init_message():
    mocked_reqparser_add_argument = Mock()
    with patch.object(reqparse.RequestParser, "add_argument",
                      new=mocked_reqparser_add_argument):
        runner = get_instance_message()

    assert isinstance(runner, ListenMessage)
    assert isinstance(runner._config, Config)
    assert isinstance(runner._logger, PythonLogger)
    mocked_reqparser_add_argument.assert_has_calls(
        [
            call('summary', location='form'),
            call('message', location='form'),
            call('hostname', location='form'),
            call('message_type', location='form'),
        ]
    )


@pytest.mark.parametrize(
    argnames=(
        "summary",
        "text",
        "message_type",
        "hostname",
        "expected_message_summary",
        "expected_message_text",
        "expected_code"
    ),
    argvalues=[
        (None, None, None, None, None, None, 400),
        (None, "I am a text message", None, None, None, None, 400),
        (None, None, None, "endor", None, None, 400),
        (
            None,
            "I am a text message",
            None,
            "endor",
            None,
            " from endor:\n\nI am a text message",
            200
        ),
        (
            None,
            "I am a text message",
            MessageType.ALARM,
            "endor",
            None,
            "4 from endor:\n\nI am a text message",
            200
        ),
        (
            "I am a summary",
            "I am a text message",
            None,
            "endor",
            " endor:\n\nI am a summary",
            "I am a text message",
            200
        ),
        (
            "I am a summary",
            "I am a text message",
            MessageType.WARNING,
            "endor",
            "2 endor:\n\nI am a summary",
            "I am a text message",
            200
        ),
        ("I am a summary", None, MessageType.WARNING, "endor", None, None, 400),
    ],
)
@patch.object(reqparse.RequestParser, "add_argument", new=patched_parser_add_argument)
@patch.object(Publisher, "__init__", new=patched_publisher_init)
@patch.object(Config, "get", new=patched_config_get)
def test_post_optional_params_not_present(
    summary,
    text,
    message_type,
    hostname,
    expected_message_summary,
    expected_message_text,
    expected_code
):
    listener = get_instance_message()

    parameters = {}
    if summary is not None:
        parameters["summary"] = summary
    if text is not None:
        parameters["message"] = text
    if message_type is not None:
        parameters["message_type"] = message_type
    if hostname is not None:
        parameters["hostname"] = hostname

    mocked_parse_args = Mock()
    mocked_parse_args.return_value = parameters
    mocked_message_init = Mock()
    mocked_message_init.__class__ = Message
    mocked_message_init.return_value = None
    mocked_publisher_publish_message = Mock()
    mocked_message_type_icon = Mock()
    mocked_message_type_icon.return_value = ICONS[message_type]\
        if message_type is not None else ""
    with patch.object(listener._parser, "parse_args", new=mocked_parse_args):
        with patch.object(MessageType, "icon_per_type", new=mocked_message_type_icon):
            with patch.object(Message, "__init__", new=mocked_message_init):
                with patch.object(Publisher,
                                  "publish_message",
                                  new=mocked_publisher_publish_message):
                    result = listener.post()

    mocked_parse_args.assert_called_once()
    if expected_code == 200:
        mocked_message_type_icon.assert_called_once_with(
            message_type if message_type else MessageType.NONE
        )
        if expected_message_summary is not None:
            mocked_message_init.assert_called_once_with(
                summary=expected_message_summary, text=expected_message_text
            )
        else:
            mocked_message_init.assert_called_once_with(text=expected_message_text)
        # For any reason I can't ensure that publish_message()
        #   is called with the mocked queue item!
        mocked_publisher_publish_message.assert_called_once()
    else:
        mocked_message_type_icon.assert_not_called()
        mocked_message_init.assert_not_called()
        mocked_publisher_publish_message.assert_not_called()

    if isinstance(result, tuple):
        return_message, code = result
    else:
        code = result

    assert code == expected_code
