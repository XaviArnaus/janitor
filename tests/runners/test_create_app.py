from pyxavi.config import Config
from pyxavi.logger import Logger
from create_app import CreateApp
from unittest.mock import patch, Mock, call
from janitor.lib.mastodon_helper import MastodonHelper
from logging import Logger as PythonLogger


def patched_generic_init(self):
    pass


def patched_generic_init_with_config(self, config):
    pass


@patch.object(Config, "__init__", new=patched_generic_init)
@patch.object(Logger, "__init__", new=patched_generic_init_with_config)
def get_instance() -> CreateApp:
    mocked_official_logger = Mock()
    mocked_official_logger.__class__ = PythonLogger
    mocked_logger_get_logger = Mock()
    mocked_logger_get_logger.return_value = mocked_official_logger
    with patch.object(Logger, "get_logger", new=mocked_logger_get_logger):
        return CreateApp()


def test_init():
    runner = get_instance()

    assert isinstance(runner, CreateApp)
    assert isinstance(runner._config, Config)
    assert isinstance(runner._logger, PythonLogger)


def test_create_app():
    instance_type = "mastodon"
    app_name = "This is my App name"
    base_url = "https://mastodont.cat"
    client_file = "client.secret"

    runner = get_instance()

    mocked_create_app = Mock()
    mocked_config_get = Mock()
    mocked_config_get.side_effect = [instance_type, app_name, base_url, client_file]
    with patch.object(MastodonHelper, "create_app", new=mocked_create_app):
        with patch.object(Config, "get", new=mocked_config_get):
            runner.run()

    mocked_create_app.assert_called_once_with(
        instance_type, app_name, api_base_url=base_url, to_file=client_file
    )
    mocked_config_get.assert_has_calls(
        [
            call("mastodon.instance_type"),
            call("mastodon.app_name"),
            call("mastodon.api_base_url"),
            call("mastodon.credentials.client_file"),
        ]
    )
