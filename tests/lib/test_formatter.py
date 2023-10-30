from pyxavi.config import Config
from janitor.lib.formatter import Formatter
from janitor.objects.message import Message, MessageType
from janitor.objects.mastodon_connection_params import MastodonStatusParams
from janitor.objects.status_post import StatusPost, StatusPostContentType, StatusPostVisibility
from unittest.mock import patch, Mock
import pytest
from unittest import TestCase
from logging import Logger

CONFIG = {
    "logger.name": "logger_test",
    "mastodon.status_post.content_type": "text/plain",
    "mastodon.status_post.visibility": "public"
}

STATUS_PARAMS = {
    "content_type": "text/plain",
    "visibility": "public",
    "max_length": 500,
    "username_to_dm": "@xavi"
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


def get_instance(status_params: MastodonStatusParams = None) -> Formatter:
    if status_params is None:
        status_params = MastodonStatusParams.from_dict(STATUS_PARAMS)
    with patch.object(Config, "__init__", new=patched_config_init):
        with patch.object(Config, "get", new=patched_config_get):
            return Formatter(config=Config(), status_params=status_params)


def test_initialize():
    formatter = get_instance()

    assert isinstance(formatter, Formatter)
    assert isinstance(formatter._config, Config)
    assert isinstance(formatter._logger, Logger)


def test_build_status_post_without_summary(message_without_summary: Message):
    status_post_content_type = StatusPostContentType.PLAIN
    status_post_visibility = StatusPostVisibility.PUBLIC
    status_params = MastodonStatusParams.from_dict(
        {
            "content_type": status_post_content_type, "visibility": status_post_visibility
        }
    )
    formatter = get_instance(status_params)

    expected_status_post = StatusPost(
        status=message_without_summary.text,
        content_type=status_post_content_type,
        visibility=status_post_visibility
    )

    mocked_add_mention = Mock()
    mocked_add_mention.return_value = message_without_summary.text
    with patch.object(formatter,
                      "add_mention_to_message_if_direct_visibility",
                      new=mocked_add_mention):
        formatted_status_post = formatter.build_status_post(message=message_without_summary)

    assert formatted_status_post.spoiler_text == expected_status_post.spoiler_text
    assert formatted_status_post.status == expected_status_post.status
    assert formatted_status_post.visibility == expected_status_post.visibility
    assert formatted_status_post.content_type == expected_status_post.content_type


def test_build_status_post_with_summary(message_with_summary: Message):
    status_post_content_type = StatusPostContentType.PLAIN
    status_post_visibility = StatusPostVisibility.PUBLIC
    status_params = MastodonStatusParams.from_dict(
        {
            "content_type": status_post_content_type, "visibility": status_post_visibility
        }
    )
    formatter = get_instance(status_params)

    expected_status_post = StatusPost(
        spoiler_text=message_with_summary.summary,
        status=message_with_summary.text,
        content_type=status_post_content_type,
        visibility=status_post_visibility
    )

    mocked_add_mention = Mock()
    mocked_add_mention.return_value = message_with_summary.text
    with patch.object(formatter,
                      "add_mention_to_message_if_direct_visibility",
                      new=mocked_add_mention):
        formatted_status_post = formatter.build_status_post(message=message_with_summary)

    assert formatted_status_post.spoiler_text == expected_status_post.spoiler_text
    assert formatted_status_post.status == expected_status_post.status
    assert formatted_status_post.visibility == expected_status_post.visibility
    assert formatted_status_post.content_type == expected_status_post.content_type


@pytest.mark.parametrize(
    argnames=('text', 'mention', 'visibility', 'expected_result'),
    argvalues=[
        ("I am a message", "@xavi", "direct", "I am a message\n\n🤫 Only for your eyes, @xavi"),
        ("I am a message", "@xavi", "private", "I am a message\n\n🤫 Only for your eyes, @xavi"),
        ("I am a message", None, "direct", False),
        ("I am a message", "@xavi", "public", "I am a message"),
    ],
)
def test_add_mention_to_message_when_is_dm(text, mention, visibility, expected_result):

    if expected_result is False:
        with TestCase.assertRaises(MastodonStatusParams, ValueError):
            status_params = MastodonStatusParams.from_dict(
                {
                    "visibility": visibility, "username_to_dm": mention
                }
            )
            formatter = get_instance(status_params)
    else:
        status_params = MastodonStatusParams.from_dict(
            {
                "visibility": visibility, "username_to_dm": mention
            }
        )
        formatter = get_instance(status_params)

        result_text = formatter.add_mention_to_message_if_direct_visibility(text=text)

        assert expected_result == result_text
