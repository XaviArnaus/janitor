from pyxavi.config import Config
from janitor.lib.mastodon_helper import MastodonHelper
from janitor.objects.mastodon_connection_params import MastodonConnectionParams
from unittest.mock import patch, Mock
from unittest import TestCase
import pytest
from mastodon import Mastodon
import os

CONFIG = {
    "logger.name": "logger_test",
    "mastodon.named_accounts.default.instance_type": "mastodon",
    "mastodon.named_accounts.default.credentials.user_file": "user.secret",
    "mastodon.named_accounts.default.credentials.client_file": "client.secret",
    "mastodon.named_accounts.default.api_base_url": "https://mastodont.cat",
    "mastodon.named_accounts.default.credentials.user.email": "bot+syscheck@my-fancy.site",
    "mastodon.named_accounts.default.credentials.user.password": "SuperSecureP4ss",
}

CONFIG_MASTODON_CONN_PARAMS = {
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


def patched_config_init(self):
    pass


def patched_config_get(self, param: str, default=None) -> str:
    return CONFIG[param]


@pytest.mark.parametrize(
    argnames=('value', 'expected_type', 'expected_exception'),
    argvalues=[
        ("mastodon", MastodonHelper.TYPE_MASTODON, False),
        ("pleroma", MastodonHelper.TYPE_PLEROMA, False),
        ("firefish", MastodonHelper.TYPE_FIREFISH, False),
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
    CONFIG_MASTODON_CONN_PARAMS["instance_type"] = "mastodon"
    mocked_path_exists = Mock()
    mocked_path_exists.return_value = True
    mocked_mastodon_init = Mock()
    mocked_mastodon_init.return_value = None
    mocked_mastodon_init.__class__ = Mastodon
    with patch.object(os.path, "exists", new=mocked_path_exists):
        with patch.object(Mastodon, "__init__", new=mocked_mastodon_init):
            conn_params = MastodonConnectionParams.from_dict(CONFIG_MASTODON_CONN_PARAMS)
            instance = MastodonHelper.get_instance(
                config=Config(), connection_params=conn_params
            )

    mocked_path_exists.assert_called_once_with(
        CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"]
    )
    mocked_mastodon_init.assert_called_once_with(
        access_token=CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"],
        feature_set="mainline"
    )
    assert isinstance(instance, Mastodon)


@patch.object(Config, "__init__", new=patched_config_init)
@patch.object(Config, "get", new=patched_config_get)
def test_get_instance_pleroma_user_credentials_exists():
    CONFIG_MASTODON_CONN_PARAMS["instance_type"] = "pleroma"
    mocked_path_exists = Mock()
    mocked_path_exists.return_value = True
    mocked_mastodon_init = Mock()
    mocked_mastodon_init.return_value = None
    mocked_mastodon_init.__class__ = Mastodon
    with patch.object(os.path, "exists", new=mocked_path_exists):
        with patch.object(Mastodon, "__init__", new=mocked_mastodon_init):
            conn_params = MastodonConnectionParams.from_dict(CONFIG_MASTODON_CONN_PARAMS)
            instance = MastodonHelper.get_instance(
                config=Config(), connection_params=conn_params
            )

    mocked_path_exists.assert_called_once_with(
        CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"]
    )
    mocked_mastodon_init.assert_called_once_with(
        access_token=CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"],
        feature_set="pleroma"
    )
    assert isinstance(instance, Mastodon)


@patch.object(Config, "__init__", new=patched_config_init)
@patch.object(Config, "get", new=patched_config_get)
def test_get_instance_mastodon_user_credentials_not_exists():
    CONFIG_MASTODON_CONN_PARAMS["instance_type"] = "mastodon"
    mocked_path_exists = Mock()
    mocked_path_exists.return_value = False
    mocked_mastodon_init = Mock()
    mocked_mastodon_init.return_value = None
    mocked_mastodon_init.__class__ = Mastodon
    mocked_mastodon_log_in = Mock()
    with patch.object(os.path, "exists", new=mocked_path_exists):
        with patch.object(Mastodon, "__init__", new=mocked_mastodon_init):
            with patch.object(Mastodon, "log_in", new=mocked_mastodon_log_in):
                conn_params = MastodonConnectionParams.from_dict(CONFIG_MASTODON_CONN_PARAMS)
                instance = MastodonHelper.get_instance(
                    config=Config(), connection_params=conn_params
                )

    mocked_path_exists.assert_called_once_with(
        CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"]
    )
    mocked_mastodon_init.assert_called_once_with(
        client_id=CONFIG_MASTODON_CONN_PARAMS["credentials"]["client_file"],
        api_base_url=CONFIG_MASTODON_CONN_PARAMS["api_base_url"],
        feature_set="mainline"
    )
    mocked_mastodon_log_in.assert_called_once_with(
        CONFIG_MASTODON_CONN_PARAMS["credentials"]["user"]["email"],
        CONFIG_MASTODON_CONN_PARAMS["credentials"]["user"]["password"],
        to_file=CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"]
    )
    assert isinstance(instance, Mastodon)


@patch.object(Config, "__init__", new=patched_config_init)
@patch.object(Config, "get", new=patched_config_get)
def test_get_instance_pleroma_user_credentials_not_exists():
    CONFIG_MASTODON_CONN_PARAMS["instance_type"] = "pleroma"
    mocked_path_exists = Mock()
    mocked_path_exists.return_value = False
    mocked_mastodon_init = Mock()
    mocked_mastodon_init.return_value = None
    mocked_mastodon_init.__class__ = Mastodon
    mocked_mastodon_log_in = Mock()
    with patch.object(os.path, "exists", new=mocked_path_exists):
        with patch.object(Mastodon, "__init__", new=mocked_mastodon_init):
            with patch.object(Mastodon, "log_in", new=mocked_mastodon_log_in):
                conn_params = MastodonConnectionParams.from_dict(CONFIG_MASTODON_CONN_PARAMS)
                instance = MastodonHelper.get_instance(
                    config=Config(), connection_params=conn_params
                )

    mocked_path_exists.assert_called_once_with(
        CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"]
    )
    mocked_mastodon_init.assert_called_once_with(
        client_id=CONFIG_MASTODON_CONN_PARAMS["credentials"]["client_file"],
        api_base_url=CONFIG_MASTODON_CONN_PARAMS["api_base_url"],
        feature_set="pleroma"
    )
    mocked_mastodon_log_in.assert_called_once_with(
        CONFIG_MASTODON_CONN_PARAMS["credentials"]["user"]["email"],
        CONFIG_MASTODON_CONN_PARAMS["credentials"]["user"]["password"],
        to_file=CONFIG_MASTODON_CONN_PARAMS["credentials"]["user_file"]
    )
    assert isinstance(instance, Mastodon)
