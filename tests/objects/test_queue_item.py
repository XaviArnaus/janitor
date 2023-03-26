from src.objects.queue_item import QueueItem
from src.objects.message import Message, MessageMedia
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
