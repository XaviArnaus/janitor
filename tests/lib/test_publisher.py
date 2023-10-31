from pyxavi.config import Config
from pyxavi.media import Media
from janitor.lib.publisher import Publisher
from janitor.lib.formatter import Formatter
from janitor.lib.queue import Queue
from janitor.objects.message import Message
from janitor.objects.queue_item import QueueItem
from janitor.objects.status_post import StatusPost
from janitor.objects.mastodon_connection_params import\
    MastodonConnectionParams, MastodonStatusParams
from mastodon import Mastodon
from unittest.mock import patch, Mock, call
import pytest
from logging import Logger
from datetime import datetime

CONFIG = {
    "logger.name": "logger_test",
    "app.run_control.dry_run": False,
    "publisher.media_storage": "storage/media/"
}

CONFIG_MASTODON_CONN_PARAMS = {
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
    }
}

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


def get_instance(mastodon_connection_params: MastodonConnectionParams = None) -> Publisher:
    _mocked_mastodon_instance.__class__ = Mastodon
    _mocked_mastodon_instance.status_post = Mock()
    _mocked_mastodon_instance.status_post.return_value = {"id": 123}
    _mocked_mastodon_instance.media_post = Mock()
    _mocked_mastodon_instance.media_post.return_value = {"id": 456}
    _mocked_queue_instance.return_value = None

    if mastodon_connection_params is None:
        mastodon_connection_params = MastodonConnectionParams.from_dict(
            CONFIG_MASTODON_CONN_PARAMS
        )

    with patch.object(Config, "__init__", new=patched_config_init):
        with patch.object(Config, "get", new=patched_config_get):
            with patch.object(Queue, "__init__", new=_mocked_queue_instance):
                with patch.object(Formatter, "__init__", new=patched_formatter_init):
                    return Publisher(
                        config=Config(),
                        mastodon=_mocked_mastodon_instance,
                        connection_params=mastodon_connection_params,
                        base_path="bla"
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


def test_publish_one_not_dry_run_pleroma(queue_item_1: QueueItem):
    status_post = StatusPost(status=queue_item_1.message.text)
    mastodon_connection_params = MastodonConnectionParams.from_dict(CONFIG_MASTODON_CONN_PARAMS)
    mastodon_connection_params.instance_type = MastodonConnectionParams.TYPE_PLEROMA
    publisher = get_instance(mastodon_connection_params=mastodon_connection_params)

    mocked_build_status_post = Mock()
    mocked_build_status_post.return_value = status_post
    mocked_config_get = Mock()
    mocked_config_get.return_value = False
    with patch.object(Formatter, "build_status_post", new=mocked_build_status_post):
        with patch.object(Config, "get", new=mocked_config_get):
            result = publisher.publish_one(queue_item_1)

    mocked_config_get.assert_called_once_with("app.run_control.dry_run")
    mocked_build_status_post.assert_called_once_with(queue_item_1.message)
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


def test_publish_one_not_dry_run_mastodon(queue_item_1: QueueItem):
    status_post = StatusPost(status=queue_item_1.message.text)
    publisher = get_instance()

    mocked_build_status_post = Mock()
    mocked_build_status_post.return_value = status_post
    mocked_config_get = Mock()
    mocked_config_get.return_value = False
    with patch.object(Formatter, "build_status_post", new=mocked_build_status_post):
        with patch.object(Config, "get", new=mocked_config_get):
            result = publisher.publish_one(queue_item_1)

    mocked_config_get.assert_called_once_with("app.run_control.dry_run")
    mocked_build_status_post.assert_called_once_with(queue_item_1.message)
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


def test_publish_one_not_dry_run_mastodon_cut_text(queue_item_long: QueueItem):
    status_post = StatusPost(status=queue_item_long.message.text)
    publisher = get_instance()

    mocked_build_status_post = Mock()
    mocked_build_status_post.return_value = status_post
    mocked_config_get = Mock()
    mocked_config_get.return_value = False
    with patch.object(Formatter, "build_status_post", new=mocked_build_status_post):
        with patch.object(Config, "get", new=mocked_config_get):
            result = publisher.publish_one(queue_item_long)

    mocked_config_get.assert_called_once_with("app.run_control.dry_run")
    mocked_build_status_post.assert_called_once_with(queue_item_long.message)
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


def test_publish_one_dry_run(queue_item_1: QueueItem):
    status_post = StatusPost(status=queue_item_1.message.text)
    publisher = get_instance()

    mocked_build_status_post = Mock()
    mocked_build_status_post.return_value = status_post
    mocked_config_get = Mock()
    mocked_config_get.return_value = True
    with patch.object(Formatter, "build_status_post", new=mocked_build_status_post):
        with patch.object(Config, "get", new=mocked_config_get):
            result = publisher.publish_one(queue_item_1)

    mocked_config_get.assert_called_once_with("app.run_control.dry_run")
    mocked_build_status_post.assert_called_once_with(queue_item_1.message)
    _mocked_mastodon_instance.status_post.assert_not_called()
    assert result is None


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
    mocked_config_get.assert_called_once_with("publisher.media_storage")
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

    mocked_queue_is_empty = Mock()
    mocked_queue_is_empty.side_effect = [False, False, False, True]
    mocked_queue_pop = Mock()
    mocked_queue_pop.side_effect = [queue_item_1, queue_item_2]
    mocked_config_dry_run = Mock()
    mocked_config_dry_run.return_value = True
    mocked_publish_one = Mock()
    with patch.object(Queue, "is_empty", new=mocked_queue_is_empty):
        with patch.object(Queue, "pop", new=mocked_queue_pop):
            with patch.object(publisher, "publish_one", new=mocked_publish_one):
                with patch.object(Config, "get", new=mocked_config_dry_run):
                    result = publisher.publish_all_from_queue()

    assert mocked_queue_is_empty.call_count == 4
    assert mocked_queue_pop.call_count == 2
    mocked_config_dry_run.assert_called_once_with("app.run_control.dry_run")
    mocked_publish_one.assert_has_calls([call(queue_item_1), call(queue_item_2)])
    assert result is None


def test_publish_all_from_queue_not_is_empty_no_dry_run(queue_item_1, queue_item_2):
    publisher = get_instance()

    mocked_queue_is_empty = Mock()
    mocked_queue_is_empty.side_effect = [False, False, False, True]
    mocked_queue_pop = Mock()
    mocked_queue_pop.side_effect = [queue_item_1, queue_item_2]
    mocked_config_dry_run = Mock()
    mocked_config_dry_run.return_value = False
    mocked_publish_one = Mock()
    mocked_queue_save = Mock()
    with patch.object(Queue, "is_empty", new=mocked_queue_is_empty):
        with patch.object(Queue, "pop", new=mocked_queue_pop):
            with patch.object(publisher, "publish_one", new=mocked_publish_one):
                with patch.object(Config, "get", new=mocked_config_dry_run):
                    with patch.object(Queue, "save", new=mocked_queue_save):
                        result = publisher.publish_all_from_queue()

    assert mocked_queue_is_empty.call_count == 4
    assert mocked_queue_pop.call_count == 2
    mocked_config_dry_run.assert_called_once_with("app.run_control.dry_run")
    mocked_publish_one.assert_has_calls([call(queue_item_1), call(queue_item_2)])
    mocked_queue_save.assert_called_once()
    assert result is None


def test_publish_older_from_queue_is_empty():
    publisher = get_instance()

    mocked_queue_is_empty = Mock()
    mocked_queue_is_empty.return_value = True
    with patch.object(Queue, "is_empty", new=mocked_queue_is_empty):
        result = publisher.publish_all_from_queue()

    mocked_queue_is_empty.assert_called_once()
    assert result is None


def test_publish_older_from_queue_not_is_empty_dry_run(queue_item_1):
    publisher = get_instance()

    mocked_queue_is_empty = Mock()
    mocked_queue_is_empty.return_value = False
    mocked_queue_pop = Mock()
    mocked_queue_pop.return_value = queue_item_1
    mocked_config_dry_run = Mock()
    mocked_config_dry_run.return_value = True
    mocked_publish_one = Mock()
    with patch.object(Queue, "is_empty", new=mocked_queue_is_empty):
        with patch.object(Queue, "pop", new=mocked_queue_pop):
            with patch.object(publisher, "publish_one", new=mocked_publish_one):
                with patch.object(Config, "get", new=mocked_config_dry_run):
                    result = publisher.publish_older_from_queue()

    mocked_queue_is_empty.assert_called_once()
    mocked_queue_pop.assert_called_once()
    mocked_config_dry_run.assert_called_once_with("app.run_control.dry_run")
    mocked_publish_one.assert_called_once_with(queue_item_1)
    assert result is None


def test_publish_older_from_queue_not_is_empty(queue_item_1):
    publisher = get_instance()

    mocked_queue_is_empty = Mock()
    mocked_queue_is_empty.return_value = False
    mocked_queue_pop = Mock()
    mocked_queue_pop.return_value = queue_item_1
    mocked_config_dry_run = Mock()
    mocked_config_dry_run.return_value = False
    mocked_publish_one = Mock()
    mocked_queue_save = Mock()
    with patch.object(Queue, "is_empty", new=mocked_queue_is_empty):
        with patch.object(Queue, "pop", new=mocked_queue_pop):
            with patch.object(publisher, "publish_one", new=mocked_publish_one):
                with patch.object(Config, "get", new=mocked_config_dry_run):
                    with patch.object(Queue, "save", new=mocked_queue_save):
                        result = publisher.publish_older_from_queue()

    mocked_queue_is_empty.assert_called_once()
    mocked_queue_pop.assert_called_once()
    mocked_config_dry_run.assert_called_once_with("app.run_control.dry_run")
    mocked_publish_one.assert_called_once_with(queue_item_1)
    mocked_queue_save.assert_called_once()
    assert result is None
