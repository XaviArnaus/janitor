from src.objects.status_post import StatusPost, StatusPostContentType, StatusPostVisibility
from unittest import TestCase
from freezegun import freeze_time
from datetime import datetime
import pytest


def test_instantiate_minimal():
    instance = StatusPost()

    assert isinstance(instance, StatusPost)


def test_instantiate_with_status():
    status_value = "I am a status"
    instance = StatusPost(status=status_value)

    assert isinstance(instance, StatusPost)
    assert instance.status, status_value


def test_instantiate_with_in_reply_to_id():
    in_reply_to_id_value = 123
    instance = StatusPost(in_reply_to_id=in_reply_to_id_value)

    assert isinstance(instance, StatusPost)
    assert instance.in_reply_to_id, in_reply_to_id_value


def test_instantiate_with_media_ids():
    media_ids_value = [12, 23]
    instance = StatusPost(media_ids=media_ids_value)

    assert isinstance(instance, StatusPost)
    assert instance.media_ids, media_ids_value


def test_instantiate_with_sensitive():
    sensitive_value = True
    instance = StatusPost(sensitive=sensitive_value)

    assert isinstance(instance, StatusPost)
    assert instance.sensitive, sensitive_value


def test_instantiate_with_sensitive_defers_to_false():
    instance = StatusPost()

    assert isinstance(instance, StatusPost)
    assert instance.sensitive == False


def test_instantiate_with_visibility():
    visibility_value = StatusPostVisibility.PUBLIC
    instance = StatusPost(visibility=visibility_value)

    assert isinstance(instance, StatusPost)
    assert instance.visibility, visibility_value


def test_instantiate_with_visibility_defers_to_public():
    instance = StatusPost()

    assert isinstance(instance, StatusPost)
    assert instance.visibility, StatusPostVisibility.PUBLIC


def test_instantiate_with_spoiler_text():
    spoiler_text_value = "I am the spoiler text"
    instance = StatusPost(spoiler_text=spoiler_text_value)

    assert isinstance(instance, StatusPost)
    assert instance.spoiler_text, spoiler_text_value


def test_instantiate_with_language():
    language_value = "ca"
    instance = StatusPost(language=language_value)

    assert isinstance(instance, StatusPost)
    assert instance.language, language_value


def test_instantiate_with_idempotency_key():
    idempotency_key_value = "abcdefghijk"
    instance = StatusPost(idempotency_key=idempotency_key_value)

    assert isinstance(instance, StatusPost)
    assert instance.idempotency_key, idempotency_key_value


def test_instantiate_with_content_type():
    content_type_value = StatusPostContentType.PLAIN
    instance = StatusPost(content_type=content_type_value)

    assert isinstance(instance, StatusPost)
    assert instance.content_type, content_type_value


def test_instantiate_with_content_type_defers_to_plain():
    instance = StatusPost()

    assert isinstance(instance, StatusPost)
    assert instance.content_type, StatusPostContentType.PLAIN


@freeze_time("2023-03-24")
def test_instantiate_with_scheduled_at():
    scheduled_at_value = datetime(2023,3,23)
    instance = StatusPost(scheduled_at=scheduled_at_value)

    assert isinstance(instance, StatusPost)
    assert instance.scheduled_at, scheduled_at_value


def test_instantiate_with_poll():
    poll_value = "whatever, the Poll object is missing, not supported"
    instance = StatusPost(poll=poll_value)

    assert isinstance(instance, StatusPost)
    assert instance.poll, poll_value


def test_instantiate_with_quote_id():
    quote_id_value = 1234
    instance = StatusPost(quote_id=quote_id_value)

    assert isinstance(instance, StatusPost)
    assert instance.quote_id, quote_id_value


@freeze_time("2023-03-24")
def test_to_dict_full():
    status_value = "I am a status"
    in_reply_to_id_value = 123
    media_ids_value = [12, 23]
    sensitive_value = True
    visibility_value = StatusPostVisibility.PUBLIC
    spoiler_text_value = "I am the spoiler text"
    language_value = "ca"
    idempotency_key_value = "abcdefghijk"
    content_type_value = StatusPostContentType.PLAIN
    scheduled_at_value = datetime(2023,3,23)
    poll_value = "whatever, the Poll object is missing, not supported"
    quote_id_value = 1234

    d = StatusPost(
        status = status_value,
        in_reply_to_id = in_reply_to_id_value,
        media_ids = media_ids_value,
        sensitive = sensitive_value,
        visibility = visibility_value,
        spoiler_text = spoiler_text_value,
        language = language_value,
        idempotency_key = idempotency_key_value,
        content_type = content_type_value,
        scheduled_at = scheduled_at_value,
        poll = poll_value,
        quote_id = quote_id_value,
    ).to_dict()

    assert d["status"], status_value
    assert d["in_reply_to_id"], in_reply_to_id_value
    assert d["media_ids"], media_ids_value
    assert d["sensitive"] == sensitive_value
    assert d["visibility"], str(visibility_value)
    assert d["spoiler_text"], spoiler_text_value
    assert d["language"], language_value
    assert d["idempotency_key"], idempotency_key_value
    assert d["content_type"], str(content_type_value)
    assert d["scheduled_at"], datetime.timestamp(scheduled_at_value)
    assert d["poll"], poll_value
    assert d["quote_id"], quote_id_value


def test_to_dict_minimal():
    d = StatusPost().to_dict()

    assert d["status"] == None
    assert d["in_reply_to_id"] == None
    assert d["media_ids"] == None
    assert d["sensitive"] == False
    assert d["visibility"] == StatusPostVisibility.PUBLIC
    assert d["spoiler_text"] == None
    assert d["language"] == None
    assert d["idempotency_key"] == None
    assert d["content_type"] == StatusPostContentType.PLAIN
    assert d["scheduled_at"] == None
    assert d["poll"] == None
    assert d["quote_id"] == None


def test_from_dict_full():
    status_value = "I am a status"
    in_reply_to_id_value = 123
    media_ids_value = [12, 23]
    sensitive_value = True
    visibility_value = StatusPostVisibility.PRIVATE
    spoiler_text_value = "I am the spoiler text"
    language_value = "ca"
    idempotency_key_value = "abcdefghijk"
    content_type_value = StatusPostContentType.MARKDOWN
    scheduled_at_value = datetime(2023,3,23)
    poll_value = "whatever, the Poll object is missing, not supported"
    quote_id_value = 1234

    status_post = StatusPost.from_dict({
        "status": status_value,
        "in_reply_to_id": in_reply_to_id_value,
        "media_ids": media_ids_value,
        "sensitive": sensitive_value,
        "visibility": visibility_value,
        "spoiler_text": spoiler_text_value,
        "language": language_value,
        "idempotency_key": idempotency_key_value,
        "content_type": content_type_value,
        "scheduled_at": datetime.timestamp(scheduled_at_value),
        "poll": poll_value,
        "quote_id": quote_id_value,
    })

    assert status_post.status == status_value
    assert status_post.in_reply_to_id == in_reply_to_id_value
    assert status_post.media_ids == media_ids_value
    assert status_post.sensitive == sensitive_value
    assert status_post.visibility == visibility_value
    assert status_post.spoiler_text == spoiler_text_value
    assert status_post.language == language_value
    assert status_post.idempotency_key == idempotency_key_value
    assert status_post.content_type == content_type_value
    assert status_post.scheduled_at == scheduled_at_value
    assert status_post.poll == poll_value
    assert status_post.quote_id == quote_id_value


def test_from_dict_minimal():
    status_post = StatusPost.from_dict({})

    assert status_post.status == None
    assert status_post.in_reply_to_id == None
    assert status_post.media_ids == None
    assert status_post.sensitive == False
    assert status_post.visibility == StatusPostVisibility.PUBLIC
    assert status_post.spoiler_text == None
    assert status_post.language == None
    assert status_post.idempotency_key == None
    assert status_post.content_type == StatusPostContentType.PLAIN
    assert status_post.scheduled_at == None
    assert status_post.poll == None
    assert status_post.quote_id == None


@pytest.mark.parametrize(
    argnames=('value', 'expected_status_post_visibility', 'expected_exception'),
    argvalues=[
        ("direct", StatusPostVisibility.DIRECT, False),
        ("private", StatusPostVisibility.PRIVATE, False),
        ("unlisted", StatusPostVisibility.UNLISTED, False),
        ("public", StatusPostVisibility.PUBLIC, False),
        ("whatever", None, RuntimeError),
    ],
)
def test_message_type_valid_or_raise(value, expected_status_post_visibility, expected_exception):
    if expected_exception:
        with TestCase.assertRaises(StatusPostVisibility, expected_exception):
            instanciated_status_post_visibility = StatusPostVisibility.valid_or_raise(value=value)
    else:
        instanciated_status_post_visibility = StatusPostVisibility.valid_or_raise(value=value)
        assert instanciated_status_post_visibility, expected_status_post_visibility


@pytest.mark.parametrize(
    argnames=('value', 'expected_status_post_content_type', 'expected_exception'),
    argvalues=[
        ("text/plain", StatusPostContentType.PLAIN, False),
        ("text/markdown", StatusPostContentType.MARKDOWN, False),
        ("text/html", StatusPostContentType.HTML, False),
        ("text/bbcode", StatusPostContentType.BBCODE, False),
        ("whatever", None, RuntimeError),
    ],
)
def test_message_type_valid_or_raise(value, expected_status_post_content_type, expected_exception):
    if expected_exception:
        with TestCase.assertRaises(StatusPostContentType, expected_exception):
            instanciated_status_post_content_type = StatusPostContentType.valid_or_raise(value=value)
    else:
        instanciated_status_post_content_type = StatusPostContentType.valid_or_raise(value=value)
        assert instanciated_status_post_content_type, expected_status_post_content_type

