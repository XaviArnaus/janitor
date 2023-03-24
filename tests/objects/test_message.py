from src.objects.message import Message, MessageType
from unittest import TestCase


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