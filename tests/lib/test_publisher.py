from pyxavi.config import Config
from pyxavi.media import Media
from janitor.lib.publisher import Publisher, PublisherException
from janitor.lib.formatter import Formatter
from janitor.lib.queue import Queue
from pyxavi.mastodon_helper import MastodonHelper, StatusPost, MastodonStatusParams
from janitor.objects.message import Message, MessageType
from janitor.objects.queue_item import QueueItem
from mastodon import Mastodon
from unittest.mock import patch, Mock, call
import pytest
from logging import Logger
from datetime import datetime

CONFIG = {
    "logger.name": "logger_test",
    "app.run_control.dry_run": False,
    "publisher.media_storage": "storage/media/",
    "publisher.only_oldest_post_every_iteration": False,
    "mastodon.named_accounts.mastodon": {
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
        },
        "status_params": {
            "max_length": 5000
        }
    },
    "mastodon.named_accounts.pleroma": {
        "app_type": "SuperApp",
        "instance_type": "pleroma",
        "api_base_url": "https://mastodont.cat",
        "credentials": {
            "user_file": "user.secret",
            "client_file": "client.secret",
            "user": {
                "email": "bot+syscheck@my-fancy.site",
                "password": "SuperSecureP4ss",
            }
        },
        "status_params": {
            "max_length": 5000
        }
    }
}

# CONFIG_MASTODON_CONN_PARAMS = {
#     "app_type": "SuperApp",
#     "instance_type": "mastodon",
#     "api_base_url": "https://mastodont.cat",
#     "credentials": {
#         "user_file": "user.secret",
#         "client_file": "client.secret",
#         "user": {
#             "email": "bot+syscheck@my-fancy.site",
#             "password": "SuperSecureP4ss",
#         }
#     },
#     "status_params": {
#         "max_length": 500
#     }
# }

_mocked_mastodon_instance: Mastodon = Mock()
_mocked_queue_instance = Mock()


def patched_config_init(self):
    pass


def patched_config_get(self, param: str, default=None) -> str:
    return CONFIG[param]


def patched_generic_init(self, config: Config):
    pass


def patched_formatter_init(self, config: Config, status_params: MastodonStatusParams):
    pass


def get_instance(named_account: str = "mastodon") -> Publisher:
    _mocked_mastodon_instance.__class__ = Mastodon
    _mocked_mastodon_instance.status_post = Mock()
    _mocked_mastodon_instance.status_post.return_value = {"id": 123}
    _mocked_mastodon_instance.media_post = Mock()
    _mocked_mastodon_instance.media_post.return_value = {"id": 456}
    _mocked_queue_instance.return_value = None

    mocked_get_mastodon_instance = Mock()
    mocked_get_mastodon_instance.return_value = _mocked_mastodon_instance
    with patch.object(Config, "__init__", new=patched_config_init):
        with patch.object(Config, "get", new=patched_config_get):
            with patch.object(Queue, "__init__", new=_mocked_queue_instance):
                with patch.object(Formatter, "__init__", new=patched_formatter_init):
                    with patch.object(MastodonHelper,
                                      "get_instance",
                                      new=mocked_get_mastodon_instance):
                        return Publisher(
                            config=Config(), named_account=named_account, base_path="bla"
                        )


def test_initialize():
    publisher = get_instance()

    assert isinstance(publisher, Publisher)
    assert isinstance(publisher._config, Config)
    assert isinstance(publisher._logger, Logger)
    assert isinstance(publisher._queue, Queue)
    assert isinstance(publisher._formatter, Formatter)
    assert isinstance(publisher._mastodon, Mastodon)


@pytest.fixture
def datetime_1():
    return datetime(2023, 3, 21)


@pytest.fixture
def datetime_2():
    return datetime(2023, 3, 22)


@pytest.fixture
def queue_item_1(datetime_1) -> QueueItem:
    return QueueItem(message=Message(text="one"), published_at=datetime_1)


@pytest.fixture
def queue_item_2(datetime_2) -> QueueItem:
    return QueueItem(message=Message(text="two"), published_at=datetime_2)


@pytest.fixture
def queue_item_long(datetime_2) -> QueueItem:
    return QueueItem(
        message=Message(
            text="""
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
                do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                Risus nullam eget felis eget nunc lobortis mattis. Convallis a
                cras semper auctor neque. Aliquet nec ullamcorper sit amet risus.
                Scelerisque purus semper eget duis at tellus at urna condimentum.
                Urna cursus eget nunc scelerisque viverra mauris. Tortor aliquam
                nulla facilisi cras fermentum odio eu feugiat. Vitae nunc sed velit
                dignissim sodales ut eu sem integer. Viverra adipiscing at in
                tellus. Nunc scelerisque viverra mauris in aliquam sem fringilla
                ut morbi. Sed tempus urna et pharetra pharetra massa massa ultricies.
                Felis imperdiet proin fermentum leo. Felis eget velit aliquet sagittis
                id consectetur purus ut faucibus. Pellentesque sit amet porttitor eget.
                Turpis tincidunt id aliquet risus feugiat in.
            """
        ),
        published_at=datetime_2
    )


def test_do_status_publish_pleroma(queue_item_1: QueueItem):
    status_post = StatusPost(status=queue_item_1.message.text)
    publisher = get_instance(named_account="pleroma")
    publisher._is_dry_run = False

    result = publisher._do_status_publish(status_post)

    _mocked_mastodon_instance.status_post.assert_called_once_with(
        status=status_post.status,
        in_reply_to_id=status_post.in_reply_to_id,
        media_ids=status_post.media_ids,
        sensitive=status_post.sensitive,
        visibility=status_post.visibility,
        spoiler_text=status_post.spoiler_text,
        language=status_post.language,
        idempotency_key=status_post.idempotency_key,
        content_type=status_post.content_type,
        scheduled_at=status_post.scheduled_at,
        poll=status_post.poll,
        quote_id=status_post.quote_id
    )
    assert result == {"id": 123}


def test_do_status_publish_mastodon(queue_item_1: QueueItem):
    status_post = StatusPost(status=queue_item_1.message.text)
    publisher = get_instance()
    publisher._is_dry_run = False

    result = publisher._do_status_publish(status_post)

    _mocked_mastodon_instance.status_post.assert_called_once_with(
        status=status_post.status,
        in_reply_to_id=status_post.in_reply_to_id,
        media_ids=status_post.media_ids,
        sensitive=status_post.sensitive,
        visibility=status_post.visibility,
        spoiler_text=status_post.spoiler_text,
        language=status_post.language,
        idempotency_key=status_post.idempotency_key,
        scheduled_at=status_post.scheduled_at,
        poll=status_post.poll,
    )
    assert result == {"id": 123}


def test_publish_status_post_not_dry_run_cut_text(queue_item_long: QueueItem):
    status_post = StatusPost(status=queue_item_long.message.text)
    publisher = get_instance()
    publisher._is_dry_run = False
    publisher._connection_params.status_params.max_length = 500

    result = publisher.publish_status_post(status_post)

    _mocked_mastodon_instance.status_post.assert_called_once_with(
        status=status_post.status[:497] + "...",
        in_reply_to_id=status_post.in_reply_to_id,
        media_ids=status_post.media_ids,
        sensitive=status_post.sensitive,
        visibility=status_post.visibility,
        spoiler_text=status_post.spoiler_text,
        language=status_post.language,
        idempotency_key=status_post.idempotency_key,
        scheduled_at=status_post.scheduled_at,
        poll=status_post.poll,
    )
    assert result == {"id": 123}


def test_publish_status_post_not_dry_run(queue_item_1: QueueItem):
    status_post = StatusPost(status=queue_item_1.message.text)
    publisher = get_instance(named_account="pleroma")
    publisher._is_dry_run = False

    mocked_build_status_post = Mock()
    mocked_build_status_post.return_value = status_post
    mocked_do_status_publish = Mock()
    mocked_do_status_publish.return_value = {"id": 123}
    with patch.object(Publisher, "_do_status_publish", new=mocked_do_status_publish):
        result = publisher.publish_status_post(status_post)

    mocked_do_status_publish.assert_called_once_with(status_post=status_post)
    assert result == {"id": 123}


def test_publish_status_post_dry_run(queue_item_1: QueueItem):
    status_post = StatusPost(status=queue_item_1.message.text)
    publisher = get_instance()
    publisher._is_dry_run = True

    result = publisher.publish_status_post(status_post)

    _mocked_mastodon_instance.status_post.assert_not_called()
    assert result is None


def test_publish_queue_item(queue_item_1: QueueItem):
    publisher = get_instance()

    mocked_publish_message = Mock()
    mocked_publish_message.return_value = {"id": 123}
    with patch.object(Publisher, "publish_message", new=mocked_publish_message):
        result = publisher.publish_queue_item(queue_item_1)

    mocked_publish_message.assert_called_once_with(message=queue_item_1.message)
    assert result == {"id": 123}


def test_publish_message_no_requeue(queue_item_1: QueueItem):
    status_post = StatusPost(status=queue_item_1.message.text)
    publisher = get_instance()

    mocked_build_status_post = Mock()
    mocked_build_status_post.return_value = status_post
    mocked_publish_status_post = Mock()
    mocked_publish_status_post.return_value = {"id": 123}
    with patch.object(Formatter, "build_status_post", new=mocked_build_status_post):
        with patch.object(Publisher, "publish_status_post", new=mocked_publish_status_post):
            result = publisher.publish_message(message=queue_item_1.message)

    mocked_build_status_post.assert_called_once_with(message=queue_item_1.message)
    mocked_publish_status_post.assert_called_once_with(status_post=status_post)
    assert result == {"id": 123}


def test_publish_message_no_requeue_exception(queue_item_1: QueueItem):
    status_post = StatusPost(status=queue_item_1.message.text)
    publisher = get_instance()

    mocked_build_status_post = Mock()
    mocked_build_status_post.return_value = status_post
    mocked_publish_status_post = Mock()
    mocked_publish_status_post.side_effect = PublisherException("test")
    mocked_queue_unpop = Mock()
    with patch.object(Formatter, "build_status_post", new=mocked_build_status_post):
        with patch.object(publisher, "publish_status_post", new=mocked_publish_status_post):
            _ = publisher.publish_message(message=queue_item_1.message)

    mocked_build_status_post.assert_called_once_with(message=queue_item_1.message)
    mocked_queue_unpop.assert_not_called()


def test_publish_message_requeue_exception(queue_item_1: QueueItem):
    status_post = StatusPost(status=queue_item_1.message.text)
    publisher = get_instance()
    publisher._is_dry_run = False

    mocked_build_status_post = Mock()
    mocked_build_status_post.return_value = status_post
    mocked_queue_unpop = Mock()
    mocked_publish_status_post = Mock()
    mocked_publish_status_post.side_effect = PublisherException("test")
    with patch.object(Formatter, "build_status_post", new=mocked_build_status_post):
        with patch.object(Queue, "unpop", new=mocked_queue_unpop):
            with patch.object(publisher, "publish_status_post", new=mocked_publish_status_post):
                _ = publisher.publish_message(
                    message=queue_item_1.message, requeue_if_fails=True
                )

    mocked_build_status_post.assert_called_once_with(message=queue_item_1.message)
    mocked_queue_unpop.assert_called_once()


def test_post_media():
    media_url = "http://hello.world/img.png"
    media_file = CONFIG["publisher.media_storage"] + "/img.png"
    media_mime = "image/png"
    description = "this is an alt text"

    publisher = get_instance()

    mocked_download_from_url = Mock()
    mocked_download_from_url.return_value = {"file": media_file, "mime_type": media_mime}
    mocked_config_get = Mock()
    mocked_config_get.return_value = CONFIG["publisher.media_storage"]
    with patch.object(Media, "download_from_url", new=mocked_download_from_url):
        with patch.object(Config, "get", new=mocked_config_get):
            result = publisher._post_media(media_file=media_url, description=description)

    mocked_download_from_url.assert_called_once_with(
        media_url, CONFIG["publisher.media_storage"]
    )
    assert result == {"id": 456}


def test_publish_all_from_queue_is_empty():
    publisher = get_instance()

    mocked_queue_is_empty = Mock()
    mocked_queue_is_empty.return_value = True
    with patch.object(Queue, "is_empty", new=mocked_queue_is_empty):
        result = publisher.publish_all_from_queue()

    mocked_queue_is_empty.assert_called_once()
    assert result is None


def test_publish_all_from_queue_not_is_empty_dry_run(queue_item_1, queue_item_2):
    publisher = get_instance()
    publisher._is_dry_run = True
    publisher._only_oldest = False

    mocked_queue_is_empty = Mock()
    mocked_queue_is_empty.side_effect = [False, False, False, True]
    mocked_queue_pop = Mock()
    mocked_queue_pop.side_effect = [queue_item_1, queue_item_2]
    mocked_publish_queue_item = Mock()
    with patch.object(Queue, "is_empty", new=mocked_queue_is_empty):
        with patch.object(Queue, "pop", new=mocked_queue_pop):
            with patch.object(publisher, "publish_queue_item", new=mocked_publish_queue_item):
                result = publisher.publish_all_from_queue()

    assert mocked_queue_is_empty.call_count == 4
    assert mocked_queue_pop.call_count == 2
    mocked_publish_queue_item.assert_has_calls([call(queue_item_1), call(queue_item_2)])
    assert result is None


def test_publish_all_from_queue_not_is_empty_dry_run_oldest(queue_item_1, queue_item_2):
    publisher = get_instance()
    publisher._is_dry_run = True
    publisher._only_oldest = True

    mocked_queue_is_empty = Mock()
    mocked_queue_is_empty.side_effect = [False, False, False, True]
    mocked_queue_pop = Mock()
    mocked_queue_pop.side_effect = [queue_item_1, queue_item_2]
    mocked_publish_queue_item = Mock()
    with patch.object(Queue, "is_empty", new=mocked_queue_is_empty):
        with patch.object(Queue, "pop", new=mocked_queue_pop):
            with patch.object(publisher, "publish_queue_item", new=mocked_publish_queue_item):
                result = publisher.publish_all_from_queue()

    assert mocked_queue_is_empty.call_count == 2
    assert mocked_queue_pop.call_count == 1
    mocked_publish_queue_item.assert_called_once_with(queue_item_1)
    assert result is None


def test_publish_all_from_queue_not_is_empty_no_dry_run(queue_item_1, queue_item_2):
    publisher = get_instance()
    publisher._is_dry_run = False
    publisher._only_oldest = False

    mocked_queue_is_empty = Mock()
    mocked_queue_is_empty.side_effect = [False, False, False, True]
    mocked_queue_pop = Mock()
    mocked_queue_pop.side_effect = [queue_item_1, queue_item_2]
    mocked_publish_queue_item = Mock()
    mocked_queue_save = Mock()
    with patch.object(Queue, "is_empty", new=mocked_queue_is_empty):
        with patch.object(Queue, "pop", new=mocked_queue_pop):
            with patch.object(publisher, "publish_queue_item", new=mocked_publish_queue_item):
                with patch.object(Queue, "save", new=mocked_queue_save):
                    result = publisher.publish_all_from_queue()

    assert mocked_queue_is_empty.call_count == 4
    assert mocked_queue_pop.call_count == 2
    mocked_publish_queue_item.assert_has_calls([call(queue_item_1), call(queue_item_2)])
    mocked_queue_save.assert_called_once()
    assert result is None


def test_publish_all_from_queue_not_is_empty_no_dry_run_oldest(queue_item_1, queue_item_2):
    publisher = get_instance()
    publisher._is_dry_run = False
    publisher._only_oldest = True

    mocked_queue_is_empty = Mock()
    mocked_queue_is_empty.side_effect = [False, False, False, True]
    mocked_queue_pop = Mock()
    mocked_queue_pop.side_effect = [queue_item_1, queue_item_2]
    mocked_publish_queue_item = Mock()
    mocked_queue_save = Mock()
    with patch.object(Queue, "is_empty", new=mocked_queue_is_empty):
        with patch.object(Queue, "pop", new=mocked_queue_pop):
            with patch.object(publisher, "publish_queue_item", new=mocked_publish_queue_item):
                with patch.object(Queue, "save", new=mocked_queue_save):
                    result = publisher.publish_all_from_queue()

    assert mocked_queue_is_empty.call_count == 2
    assert mocked_queue_pop.call_count == 1
    mocked_publish_queue_item.assert_called_once_with(queue_item_1)
    mocked_queue_save.assert_called_once()
    assert result is None


@pytest.mark.parametrize(
    argnames=('content', 'summary', 'method', 'expected_message_type'),
    argvalues=[
        ("I am a message", "I am a summary", "text", MessageType.NONE),
        ("I am a message", "I am a summary", "info", MessageType.INFO),
        ("I am a message", "I am a summary", "warning", MessageType.WARNING),
        ("I am a message", "I am a summary", "error", MessageType.ERROR),
        ("I am a message", "I am a summary", "alarm", MessageType.ALARM),
    ],
)
def test_shortcut(content, summary, method, expected_message_type):
    publisher = get_instance()

    mock_publish_message = Mock()
    with patch.object(publisher, "publish_message", new=mock_publish_message):
        _ = getattr(publisher, method)(content=content, summary=summary)

    called_message = mock_publish_message.call_args[1]["message"]
    assert isinstance(called_message, Message)
    assert called_message.summary == summary
    assert called_message.text == content
    assert called_message.message_type == expected_message_type


def patch_queue_load(self):
    self._queue = []


def test_reload_queue():
    publisher = get_instance()

    publisher._queue.append("one")
    publisher._queue.append("two")

    assert publisher._queue.length() == 2

    with patch.object(Queue, "load", new=patch_queue_load):
        assert publisher.reload_queue() == -2
    assert publisher._queue.length() == 0
