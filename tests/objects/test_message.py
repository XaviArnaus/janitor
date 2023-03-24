from src.objects.message import Message, MessageType, MessageMedia
from unittest import TestCase
import pytest


def test_instantiate_minimal():
    instance = Message()

    assert isinstance(instance, Message)


def test_instantiate_with_summary():
    summary_value = "I am a summary"
    instance = Message(summary=summary_value)

    assert isinstance(instance, Message)
    assert instance.summary, summary_value


def test_instantiate_with_text():
    text_value = "I am a text"
    instance = Message(text=text_value)

    assert isinstance(instance, Message)
    assert instance.text, text_value


def test_instance_with_type():
    message_type_value = MessageType.INFO
    instance = Message(message_type=message_type_value)

    assert isinstance(instance, Message)
    assert isinstance(instance.message_type, MessageType)


def test_instance_without_type_defers_to_type_none():
    instance = Message()

    assert isinstance(instance, Message)
    assert instance.message_type, MessageType.NONE


def test_to_dict_full():
    summary_value = "I am a summary"
    text_value = "I am a text"
    message_type_value = MessageType.INFO


    d = Message(
        summary=summary_value,
        text=text_value,
        message_type=message_type_value
    ).to_dict()

    assert d["summary"], summary_value
    assert d["text"], text_value
    assert d["message_type"], str(message_type_value)


def test_to_dict_minimal():
    d = Message().to_dict()

    assert d["summary"] == None
    assert d["text"] == None
    assert d["message_type"] == str(MessageType.NONE)


def test_from_dict_full():
    summary_value = "I am a summary"
    text_value = "I am a text"
    message_type_value = MessageType.INFO

    message = Message.from_dict({
        "summary": summary_value,
        "text": text_value,
        "message_type": str(message_type_value)
    })

    assert message.summary, summary_value
    assert message.text, text_value
    assert message.message_type, message_type_value


def test_from_dict_minimal():
    message = Message.from_dict({})

    assert message.summary == None
    assert message.text == None
    assert message.message_type, MessageType.NONE


@pytest.mark.parametrize(
    argnames=('value', 'expected_message_type', 'expected_exception'),
    argvalues=[
        ("none", MessageType.NONE, False),
        ("info", MessageType.INFO, False),
        ("warning", MessageType.WARNING, False),
        ("error", MessageType.ERROR, False),
        ("alarm", MessageType.ALARM, False),
        ("exception", None, RuntimeError),
    ],
)
def test_message_type_valid_or_raise(value, expected_message_type, expected_exception):
    if expected_exception:
        with TestCase.assertRaises(MessageType, expected_exception):
            instanciated_message_type = MessageType.valid_or_raise(value=value)
    else:
        instanciated_message_type = MessageType.valid_or_raise(value=value)
        assert instanciated_message_type, expected_message_type


def test_message_type_priority():
    expected = [MessageType.NONE, MessageType.INFO, MessageType.WARNING, MessageType.ERROR, MessageType.ALARM]

    assert MessageType.priority, expected


@pytest.mark.parametrize(
    argnames=('message_type', 'expected_icon', 'expected_exception'),
    argvalues=[
        (MessageType.NONE, "", False),
        (MessageType.INFO, "ℹ️", False),
        (MessageType.WARNING, "⚠️", False),
        (MessageType.ERROR, "🔥", False),
        (MessageType.ALARM, "🚨", False),
        ("exception", "", RuntimeError),
    ],
)
def test_message_type_icon_per_type(message_type, expected_icon, expected_exception):
    if expected_exception:
        with TestCase.assertRaises(MessageType, expected_exception):
            icon = MessageType.icon_per_type(message_type=message_type)
    else:
        icon = MessageType.icon_per_type(message_type=message_type)
        assert icon == expected_icon


def test_media_instantiate_minimal():
    instance = MessageMedia()

    assert isinstance(instance, MessageMedia)


def test_media_instantiate_with_url():
    url_value = "http://hello.world"
    instance = MessageMedia(url=url_value)

    assert isinstance(instance, MessageMedia)
    assert instance.url, url_value


def test_media_instantiate_with_alt_text():
    alt_text_value = "I am an alt text"
    instance = MessageMedia(alt_text=alt_text_value)

    assert isinstance(instance, MessageMedia)
    assert instance.alt_text, alt_text_value


def test_media_to_dict_full():
    url_value = "http://hello.world"
    alt_text_value = "I am an alt text"

    d = MessageMedia(
        url=url_value,
        alt_text=alt_text_value
    ).to_dict()

    assert d["url"], url_value
    assert d["alt_text"], alt_text_value


def test_media_to_dict_minimal():
    d = MessageMedia().to_dict()

    assert d["url"] == None
    assert d["alt_text"] == None


def test_media_from_dict_full():
    url_value = "http://hello.world"
    alt_text_value = "I am an alt text"

    message_media = MessageMedia.from_dict({
        "url": url_value,
        "alt_text": alt_text_value
    })

    assert message_media.url, url_value
    assert message_media.alt_text, alt_text_value


def test_media_from_dict_minimal():
    message_media = MessageMedia.from_dict({})

    assert message_media.url == None
    assert message_media.alt_text == None