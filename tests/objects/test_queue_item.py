from pyxavi.item_queue import Queue
from janitor.objects.queue_item import QueueItem
from janitor.objects.message import Message, MessageMedia
from freezegun import freeze_time
from datetime import datetime


def test_instantiate_minimal():
    instance = QueueItem()

    assert isinstance(instance, QueueItem)


def test_instantiate_with_message():
    message = Message()
    instance = QueueItem(message=message)

    assert isinstance(instance, QueueItem)
    assert isinstance(instance.message, Message)


def test_instantiate_with_media():
    message_media = MessageMedia()
    instance = QueueItem(media=[message_media])

    assert isinstance(instance, QueueItem)
    assert isinstance(instance.media, list)
    assert isinstance(instance.media[0], MessageMedia)


@freeze_time("2023-03-24")
def test_no_published_at_defers_to_now():
    instance = QueueItem()

    assert instance.published_at == datetime.now()


def test_published_injected_param():
    instance = QueueItem(published_at=datetime(2023, 3, 23))

    assert instance.published_at == datetime(2023, 3, 23)


def test_to_dict():
    message = Message(text="this is a test")
    media = [MessageMedia("http://hello.world")]
    published_at = datetime(2023, 3, 23)

    d = QueueItem(message=message, media=media, published_at=published_at).to_dict()

    # Injected objects must have their own to_dict() method.
    # Won't test them here, should have their own test
    assert d["message"]["text"] == message.text
    assert d["media"][0]["url"] == media[0].url
    assert d["published_at"] == datetime.timestamp(published_at)


def test_from_dict():
    message = Message(text="this is a test")
    media = [MessageMedia("http://hello.world")]
    published_at = datetime(2023, 3, 23)

    queue_item = QueueItem.from_dict(
        {
            "message": {
                "text": message.text
            },
            "media": [{
                "url": media[0].url
            }],
            "published_at": datetime.timestamp(published_at)
        }
    )

    # Injected objects must have their own from_dict() method.
    # Won't test them here, should have their own test
    assert queue_item.message.text == message.text
    assert queue_item.media[0].url == media[0].url
    assert queue_item.published_at == published_at


def test_sorting_uses_published_at_field():
    instance1 = QueueItem(published_at=datetime(2023, 3, 23))
    instance2 = QueueItem(published_at=datetime(2023, 4, 23))
    instance3 = QueueItem(published_at=datetime(2023, 5, 23))

    queue = Queue()

    queue.append(instance3)
    queue.append(instance1)
    queue.append(instance2)
    queue.sort()

    items = queue.get_all()
    assert items[0] == instance1
    assert items[1] == instance2
    assert items[2] == instance3


def test_deduplication_uses_message_text_and_summary_field():
    instance1 = QueueItem(Message(text="aa"))
    instance2 = QueueItem(Message(text="aa", summary="bb"))
    instance3 = QueueItem(Message(text="aa", summary="cc"))
    instance4 = QueueItem(Message(text="aa", summary="bb"))
    instance5 = QueueItem(Message(text="bb", summary="aa"))

    queue = Queue()

    queue.append(instance1)
    queue.append(instance2)
    queue.append(instance3)
    queue.append(instance4)
    queue.append(instance5)
    queue.deduplicate()

    # dd(queue._queue, max_depth=3)

    assert queue.length() == 4
    items = queue.get_all()
    assert items[0] == instance1
    assert items[1] == instance2
    assert items[2] == instance3
    assert items[3] == instance5
