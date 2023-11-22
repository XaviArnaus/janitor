from pyxavi.config import Config
from pyxavi.mastodon_publisher import MastodonPublisher, MastodonPublisherException
from janitor.lib.publisher import Publisher
from janitor.lib.formatter import Formatter
from pyxavi.item_queue import Queue
from pyxavi.mastodon_helper import MastodonHelper, StatusPost, MastodonStatusParams
from janitor.objects.message import Message, MessageType
from janitor.objects.queue_item import QueueItem
from mastodon import Mastodon
from unittest.mock import patch, Mock, call
import pytest
from logging import Logger
from datetime import datetime
import copy

CONFIG = {
    "logger": {
        "name": "logger_test"
    },
    "app": {
        "run_control": {
            "dry_run": False
        }
    },
    "publisher": {
        "media_storage": "storage/media/",
        "named_account": "test",
        "only_oldest_post_every_iteration": False
    },
    "mastodon": {
        "named_accounts": {
            "test": {
                "app_name": "Test",
                "instance_type": "firefish",
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
                    "max_length": 500
                }
            }
        }
    }
}


def patched_formatter_init(self, config: Config, status_params: MastodonStatusParams):
    pass


@pytest.fixture(autouse=True)
def setup_function():

    global CONFIG, _mocked_queue_instance, _mocked_mastodon_instance

    _mocked_queue_instance = Mock()
    _mocked_queue_instance.return_value = None
    _mocked_mastodon_instance = Mock()
    _mocked_mastodon_instance.__class__ = Mastodon

    backup = copy.deepcopy(CONFIG)

    yield

    CONFIG = backup


def patch_config_read_file(self):
    self._content = CONFIG


def patch_mastodon_get_instance(connection_params, logger=None, base_path=None) -> Mastodon:
    return _mocked_mastodon_instance


@patch.object(Config, "read_file", new=patch_config_read_file)
@patch.object(MastodonHelper, "get_instance", new=patch_mastodon_get_instance)
def get_instance() -> Publisher:
    named_account = "test"
    with patch.object(Queue, "__init__", new=_mocked_queue_instance):
        with patch.object(Formatter, "__init__", new=patched_formatter_init):
            return Publisher(config=Config(), named_account=named_account, base_path="bla")


def test_initialize():
    publisher = get_instance()

    assert isinstance(publisher, Publisher)
    assert isinstance(publisher, MastodonPublisher)
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
    mocked_publish_status_post.side_effect = MastodonPublisherException("test")
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
    mocked_publish_status_post.side_effect = MastodonPublisherException("test")
    with patch.object(Formatter, "build_status_post", new=mocked_build_status_post):
        with patch.object(Queue, "unpop", new=mocked_queue_unpop):
            with patch.object(publisher, "publish_status_post", new=mocked_publish_status_post):
                _ = publisher.publish_message(
                    message=queue_item_1.message, requeue_if_fails=True
                )

    mocked_build_status_post.assert_called_once_with(message=queue_item_1.message)
    mocked_queue_unpop.assert_called_once()


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
