from pyxavi.config import Config
from src.lib.formatter import Formatter
from src.objects.message import Message, MessageType
from src.objects.status_post import StatusPost, StatusPostContentType, StatusPostVisibility
from unittest.mock import patch, Mock, call
import pytest
from logging import Logger

CONFIG = {
    "logger.name": "logger_test",
    "status_post.content_type": "text/plain",
    "status_post.visibility": "public"
}


def patched_config_init(self):
    pass


def patched_config_get(self, param: str, default=None) -> str:
    return CONFIG[param]


@pytest.fixture
def message_without_summary() -> Message:
    return Message(text="this is the text", message_type=MessageType.WARNING)


@pytest.fixture
def message_with_summary() -> Message:
    return Message(
        summary="this is the summary",
        text="this is the text",
        message_type=MessageType.WARNING
    )


def get_instance() -> Formatter:

    with patch.object(Config, "__init__", new=patched_config_init):
        with patch.object(Config, "get", new=patched_config_get):
            return Formatter(config=Config())


def test_initialize():
    formatter = get_instance()

    assert isinstance(formatter, Formatter)
    assert isinstance(formatter._config, Config)
    assert isinstance(formatter._logger, Logger)


def test_build_status_post_without_summary(message_without_summary: Message):
    status_post_content_type = StatusPostContentType.PLAIN
    status_post_visibility = StatusPostVisibility.PUBLIC
    formatter = get_instance()

    expected_status_post = StatusPost(
        status=message_without_summary.text,
        content_type=status_post_content_type,
        visibility=status_post_visibility
    )

    mocked_config_get = Mock()
    mocked_config_get.side_effect = [
        CONFIG["status_post.content_type"], CONFIG["status_post.visibility"]
    ]
    with patch.object(Config, "get", new=mocked_config_get):
        formatted_status_post = formatter.build_status_post(message=message_without_summary)

    mocked_config_get.assert_has_calls(
        [
            call("status_post.content_type"),
            call("status_post.visibility"),
        ]
    )
    assert formatted_status_post.spoiler_text == expected_status_post.spoiler_text
    assert formatted_status_post.status == expected_status_post.status
    assert formatted_status_post.visibility == expected_status_post.visibility
    assert formatted_status_post.content_type == expected_status_post.content_type
