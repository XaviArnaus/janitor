from pyxavi.config import Config
from janitor.lib.formatter import Formatter
from janitor.objects.message import Message, MessageType
from janitor.objects.status_post import StatusPost, StatusPostContentType, StatusPostVisibility
from unittest.mock import patch, Mock, call
import pytest
from logging import Logger

CONFIG = {
    "logger.name": "logger_test",
    "mastodon.status_post.content_type": "text/plain",
    "mastodon.status_post.visibility": "public"
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
        CONFIG["mastodon.status_post.content_type"], CONFIG["mastodon.status_post.visibility"]
    ]
    mocked_add_mention = Mock()
    mocked_add_mention.return_value = message_without_summary.text
    with patch.object(Config, "get", new=mocked_config_get):
        with patch.object(formatter,
                          "add_mention_to_message_if_direct_visibility",
                          new=mocked_add_mention):
            formatted_status_post = formatter.build_status_post(message=message_without_summary)

    mocked_config_get.assert_has_calls(
        [
            call("mastodon.status_post.content_type"),
            call("mastodon.status_post.visibility"),
        ]
    )
    assert formatted_status_post.spoiler_text == expected_status_post.spoiler_text
    assert formatted_status_post.status == expected_status_post.status
    assert formatted_status_post.visibility == expected_status_post.visibility
    assert formatted_status_post.content_type == expected_status_post.content_type


def test_build_status_post_with_summary(message_with_summary: Message):
    status_post_content_type = StatusPostContentType.PLAIN
    status_post_visibility = StatusPostVisibility.PUBLIC
    formatter = get_instance()

    expected_status_post = StatusPost(
        spoiler_text=message_with_summary.summary,
        status=message_with_summary.text,
        content_type=status_post_content_type,
        visibility=status_post_visibility
    )

    mocked_config_get = Mock()
    mocked_config_get.side_effect = [
        CONFIG["mastodon.status_post.content_type"], CONFIG["mastodon.status_post.visibility"]
    ]
    mocked_add_mention = Mock()
    mocked_add_mention.return_value = message_with_summary.text
    with patch.object(Config, "get", new=mocked_config_get):
        with patch.object(formatter,
                          "add_mention_to_message_if_direct_visibility",
                          new=mocked_add_mention):
            formatted_status_post = formatter.build_status_post(message=message_with_summary)

    mocked_config_get.assert_has_calls(
        [
            call("mastodon.status_post.content_type"),
            call("mastodon.status_post.visibility"),
        ]
    )
    assert formatted_status_post.spoiler_text == expected_status_post.spoiler_text
    assert formatted_status_post.status == expected_status_post.status
    assert formatted_status_post.visibility == expected_status_post.visibility
    assert formatted_status_post.content_type == expected_status_post.content_type


@pytest.mark.parametrize(
    argnames=('text', 'mention', 'visibility', 'expected_result'),
    argvalues=[
        ("I am a message", "@xavi", "direct", "@xavi:\n\nI am a message"),
        ("I am a message", None, "direct", "I am a message"),
        ("I am a message", "@xavi", "public", "I am a message"),
    ],
)
def test_add_mention_to_message_when_is_dm(text, mention, visibility, expected_result):

    formatter = get_instance()

    mocked_config_get = Mock()
    mocked_config_get.side_effect = [visibility, mention]
    with patch.object(Config, "get", new=mocked_config_get):
        result_text = formatter.add_mention_to_message_if_direct_visibility(text=text)

    mocked_config_get.assert_has_calls(
        [call("mastodon.status_post.visibility"), call("mastodon.status_post.username_to_dm")]
    )
    assert expected_result == result_text
