from pyxavi.config import Config
from pyxavi.storage import Storage
from janitor.lib.queue import Queue
from janitor.objects.queue_item import QueueItem
from janitor.objects.message import Message
from unittest.mock import patch, Mock
import pytest
from logging import Logger
from datetime import datetime
import os

CONFIG = {"logger.name": "logger_test", "queue_storage.file": "queue.yaml"}


def patched_config_init(self):
    pass


def patched_config_get(self, param: str, default=None) -> str:
    return CONFIG[param]


def patched_storage_init(self, filename):
    pass


def patched_storage_write(self):
    pass


def patched_storage_get(self, param_name: str = "", default_value: any = None) -> any:
    return []


@pytest.fixture
def datetime_1():
    return datetime(2023, 3, 21)


@pytest.fixture
def datetime_2():
    return datetime(2023, 3, 22)


@pytest.fixture
def datetime_3():
    return datetime(2023, 3, 23)


@pytest.fixture
def queue_item_1(datetime_1):
    return QueueItem(message=Message(text="one"), published_at=datetime_1)


@pytest.fixture
def queue_item_2(datetime_2):
    return QueueItem(message=Message(text="two"), published_at=datetime_2)


@pytest.fixture
def queue_item_3(datetime_3):
    return QueueItem(message=Message(text="three"), published_at=datetime_3)


def get_instance() -> Queue:
    with patch.object(Config, "__init__", new=patched_config_init):
        with patch.object(Config, "get", new=patched_config_get):
            with patch.object(Storage, "__init__", new=patched_storage_init):
                with patch.object(Storage, "get", new=patched_storage_get):
                    return Queue(config=Config())


def test_initialize():
    queue = get_instance()

    assert isinstance(queue, Queue)
    assert isinstance(queue._config, Config)
    assert isinstance(queue._logger, Logger)
    assert isinstance(queue._queue_manager, Storage)
    assert isinstance(queue._queue, list)


def test_initialize_with_base_path():
    mocked_storage_init = Mock()
    mocked_storage_init.return_value = None
    with patch.object(Config, "__init__", new=patched_config_init):
        with patch.object(Config, "get", new=patched_config_get):
            with patch.object(Storage, "__init__", new=mocked_storage_init):
                with patch.object(Storage, "get", new=patched_storage_get):
                    queue = Queue(config=Config(), base_path="bla")

    assert isinstance(queue, Queue)
    assert isinstance(queue._config, Config)
    assert isinstance(queue._logger, Logger)
    assert isinstance(queue._queue_manager, Storage)
    assert isinstance(queue._queue, list)
    mocked_storage_init.assert_called_once_with(filename=os.path.join("bla", "queue.yaml"))


def test_append():
    queue = get_instance()
    queue_item = QueueItem()

    expected_queue = [queue_item]
    queue.append(queue_item)

    assert queue._queue == expected_queue


def test_sort_by_date(queue_item_1, queue_item_2, queue_item_3):
    queue = get_instance()
    queue.append(queue_item_1)
    queue.append(queue_item_3)
    queue.append(queue_item_2)

    current_sorting = list(map(lambda x: x.message.text, queue._queue))
    assert current_sorting, ["one", "three", "two"]

    queue.sort_by_date()
    new_sorting = list(map(lambda x: x.message.text, queue._queue))
    assert new_sorting, ["one", "two", "three"]


def test_deduplicate(queue_item_1, queue_item_2, queue_item_3):
    queue = get_instance()
    queue.append(queue_item_1)
    queue.append(queue_item_2)
    queue.append(queue_item_2)
    queue.append(queue_item_3)

    current_queue = list(map(lambda x: x.message.text, queue._queue))
    assert current_queue, ["one", "two", "two", "three"]

    queue.deduplicate()
    new_queue = list(map(lambda x: x.message.text, queue._queue))
    assert new_queue, ["one", "two", "three"]


def test_save(datetime_1, datetime_2, datetime_3, queue_item_1, queue_item_2, queue_item_3):
    queue = get_instance()
    queue.append(queue_item_1)
    queue.append(queue_item_2)
    queue.append(queue_item_3)

    mocked_set = Mock()
    mocked_write = Mock()
    with patch.object(Storage, "set", new=mocked_set):
        with patch.object(Storage, "write_file", new=mocked_write):
            queue.save()

    mocked_set.assert_called_once_with(
        "queue",
        [
            {
                "message": {
                    "summary": None, "text": "one", "message_type": "none"
                },
                "media": None,
                "published_at": datetime.timestamp(datetime_1)
            },
            {
                "message": {
                    "summary": None, "text": "two", "message_type": "none"
                },
                "media": None,
                "published_at": datetime.timestamp(datetime_2)
            },
            {
                "message": {
                    "summary": None, "text": "three", "message_type": "none"
                },
                "media": None,
                "published_at": datetime.timestamp(datetime_3)
            }
        ]
    )
    mocked_write.assert_called_once()


def test_update():
    queue = get_instance()

    mocked_sort = Mock()
    mocked_deduplicate = Mock()
    mocked_save = Mock()
    with patch.object(Queue, "sort_by_date", new=mocked_sort):
        with patch.object(Queue, "deduplicate", new=mocked_deduplicate):
            with patch.object(Queue, "save", new=mocked_save):
                queue.update()

    mocked_sort.assert_called_once()
    mocked_deduplicate.assert_called_once()
    mocked_save.assert_called_once()


def test_is_empty(queue_item_1):
    queue = get_instance()

    assert queue.is_empty() is True

    queue.append(queue_item_1)

    assert queue.is_empty() is False

    queue._queue = []

    assert queue.is_empty() is True


def test_get_all(queue_item_1, queue_item_2, queue_item_3):
    queue = get_instance()
    queue.append(queue_item_1)
    queue.append(queue_item_2)
    queue.append(queue_item_3)

    current_queue = list(map(lambda x: x.message.text, queue.get_all()))
    assert current_queue, ["one", "two", "three"]


def test_clean(queue_item_1, queue_item_2, queue_item_3):
    queue = get_instance()
    queue.append(queue_item_1)
    queue.append(queue_item_2)
    queue.append(queue_item_3)

    assert len(queue.get_all()), 3

    queue.clean()

    assert queue.is_empty() is True


def test_pop(queue_item_1, queue_item_2, queue_item_3):
    queue = get_instance()
    queue.append(queue_item_1)
    queue.append(queue_item_2)
    queue.append(queue_item_3)

    assert len(queue.get_all()), 3

    mocked_get_dry_run = Mock()
    mocked_get_dry_run.return_value = False
    with patch.object(Config, "get", new=mocked_get_dry_run):
        queue_item = queue.pop()

    assert queue_item, queue_item_1
    assert len(queue.get_all()), 2


def test_unpop(queue_item_1, queue_item_2, queue_item_3):
    queue = get_instance()
    queue.append(queue_item_1)
    queue.append(queue_item_2)

    assert len(queue.get_all()), 2

    mocked_get_dry_run = Mock()
    mocked_get_dry_run.return_value = False
    with patch.object(Config, "get", new=mocked_get_dry_run):
        queue.unpop(item=queue_item_3)

    stack = queue.get_all()
    assert len(stack), 3
    # The unpop() should add it at the beginning
    assert stack[0] == queue_item_3
    assert stack[1] == queue_item_1
    assert stack[2] == queue_item_2
