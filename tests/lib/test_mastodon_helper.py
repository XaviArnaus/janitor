from pyxavi.config import Config
from janitor.lib.mastodon_helper import MastodonHelper
from unittest.mock import patch, Mock
from unittest import TestCase
import pytest
from mastodon import Mastodon
import os

CONFIG = {
    "logger.name": "logger_test",
    "mastodon.instance_type": "mastodon",
    "mastodon.credentials.user_file": "user.secret",
    "mastodon.credentials.client_file": "client.secret",
    "mastodon.api_base_url": "https://mastodont.cat",
    "mastodon.credentials.user.email": "bot+syscheck@my-fancy.site",
    "mastodon.credentials.user.password": "SuperSecureP4ss",
}


def patched_config_init(self):
    pass


def patched_config_get(self, param: str, default=None) -> str:
    return CONFIG[param]


@pytest.mark.parametrize(
    argnames=('value', 'expected_type', 'expected_exception'),
    argvalues=[
        ("mastodon", MastodonHelper.TYPE_MASTODON, False),
        ("pleroma", MastodonHelper.TYPE_PLEROMA, False),
        ("exception", None, RuntimeError),
    ],
)
def test_message_type_valid_or_raise(value, expected_type, expected_exception):
    if expected_exception:
        with TestCase.assertRaises(MastodonHelper, expected_exception):
            instanciated_type = MastodonHelper.valid_or_raise(value=value)
    else:
        instanciated_type = MastodonHelper.valid_or_raise(value=value)
        assert instanciated_type, expected_type


@patch.object(Config, "__init__", new=patched_config_init)
@patch.object(Config, "get", new=patched_config_get)
def test_get_instance_mastodon_user_credentials_exists():
    CONFIG["mastodon.instance_type"] = "mastodon"
    mocked_path_exists = Mock()
    mocked_path_exists.return_value = True
    mocked_mastodon_init = Mock()
    mocked_mastodon_init.return_value = None
    mocked_mastodon_init.__class__ = Mastodon
    with patch.object(os.path, "exists", new=mocked_path_exists):
        with patch.object(Mastodon, "__init__", new=mocked_mastodon_init):
            instance = MastodonHelper.get_instance(config=Config())

    mocked_path_exists.assert_called_once_with(CONFIG["mastodon.credentials.user_file"])
    mocked_mastodon_init.assert_called_once_with(
        access_token=CONFIG["mastodon.credentials.user_file"], feature_set="mainline"
    )
    assert isinstance(instance, Mastodon)


@patch.object(Config, "__init__", new=patched_config_init)
@patch.object(Config, "get", new=patched_config_get)
def test_get_instance_pleroma_user_credentials_exists():
    CONFIG["mastodon.instance_type"] = "pleroma"
    mocked_path_exists = Mock()
    mocked_path_exists.return_value = True
    mocked_mastodon_init = Mock()
    mocked_mastodon_init.return_value = None
    mocked_mastodon_init.__class__ = Mastodon
    with patch.object(os.path, "exists", new=mocked_path_exists):
        with patch.object(Mastodon, "__init__", new=mocked_mastodon_init):
            instance = MastodonHelper.get_instance(config=Config())

    mocked_path_exists.assert_called_once_with(CONFIG["mastodon.credentials.user_file"])
    mocked_mastodon_init.assert_called_once_with(
        access_token=CONFIG["mastodon.credentials.user_file"], feature_set="pleroma"
    )
    assert isinstance(instance, Mastodon)


@patch.object(Config, "__init__", new=patched_config_init)
@patch.object(Config, "get", new=patched_config_get)
def test_get_instance_mastodon_user_credentials_not_exists():
    CONFIG["mastodon.instance_type"] = "mastodon"
    mocked_path_exists = Mock()
    mocked_path_exists.return_value = False
    mocked_mastodon_init = Mock()
    mocked_mastodon_init.return_value = None
    mocked_mastodon_init.__class__ = Mastodon
    mocked_mastodon_log_in = Mock()
    with patch.object(os.path, "exists", new=mocked_path_exists):
        with patch.object(Mastodon, "__init__", new=mocked_mastodon_init):
            with patch.object(Mastodon, "log_in", new=mocked_mastodon_log_in):
                instance = MastodonHelper.get_instance(config=Config())

    mocked_path_exists.assert_called_once_with(CONFIG["mastodon.credentials.user_file"])
    mocked_mastodon_init.assert_called_once_with(
        client_id=CONFIG["mastodon.credentials.client_file"],
        api_base_url=CONFIG["mastodon.api_base_url"],
        feature_set="mainline"
    )
    mocked_mastodon_log_in.assert_called_once_with(
        CONFIG["mastodon.credentials.user.email"],
        CONFIG["mastodon.credentials.user.password"],
        to_file=CONFIG["mastodon.credentials.user_file"]
    )
    assert isinstance(instance, Mastodon)


@patch.object(Config, "__init__", new=patched_config_init)
@patch.object(Config, "get", new=patched_config_get)
def test_get_instance_pleroma_user_credentials_not_exists():
    CONFIG["mastodon.instance_type"] = "pleroma"
    mocked_path_exists = Mock()
    mocked_path_exists.return_value = False
    mocked_mastodon_init = Mock()
    mocked_mastodon_init.return_value = None
    mocked_mastodon_init.__class__ = Mastodon
    mocked_mastodon_log_in = Mock()
    with patch.object(os.path, "exists", new=mocked_path_exists):
        with patch.object(Mastodon, "__init__", new=mocked_mastodon_init):
            with patch.object(Mastodon, "log_in", new=mocked_mastodon_log_in):
                instance = MastodonHelper.get_instance(config=Config())

    mocked_path_exists.assert_called_once_with(CONFIG["mastodon.credentials.user_file"])
    mocked_mastodon_init.assert_called_once_with(
        client_id=CONFIG["mastodon.credentials.client_file"],
        api_base_url=CONFIG["mastodon.api_base_url"],
        feature_set="pleroma"
    )
    mocked_mastodon_log_in.assert_called_once_with(
        CONFIG["mastodon.credentials.user.email"],
        CONFIG["mastodon.credentials.user.password"],
        to_file=CONFIG["mastodon.credentials.user_file"]
    )
    assert isinstance(instance, Mastodon)
