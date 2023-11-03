from pyxavi.config import Config
from pyxavi.logger import Logger
from pyxavi.storage import Storage
from pyxavi.network import Network
from janitor.runners.update_ddns import UpdateDdns
from unittest.mock import patch, Mock
from definitions import ROOT_DIR
import requests
import logging
import os

# This runner tests tries to be an integration test
#   Therefore we have quite some patches / mocks

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
        "media_storage": "storage/media/", "only_oldest_post_every_iteration": False
    },
    "mastodon": {
        "named_accounts": {
            "default": {
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
            }
        }
    },
    "directnic_ddns": {
        "file": "storage/external_ip.yaml", "updates": ["url/1?param="]
    },
    "queue_storage": {
        "file": "storage/queue.yaml"
    }
}

EXTERNAL_IP = "1.2.3.4"

STORAGE_PER_FILENAME = {
    f"{ROOT_DIR}/storage/external_ip.yaml": {
        "last_external_ip": "89.247.157.10"
    },
    f"{ROOT_DIR}/storage/queue.yaml": {
        "queue": []
    }
}

mocked_response = Mock()
mocked_response.__class__ = requests.Response


def patched_config_read_file(self) -> Config:
    self._content = CONFIG


def patched_logger_init(self, config: Config) -> Logger:
    pass


def patched_logger_get_logger(self) -> logging:
    return logging.getLogger(CONFIG["logger"]["name"])


def patched_network_get_external_ip(logger: logging) -> str:
    return EXTERNAL_IP


def patched_request_get_200(url: str) -> requests.Response:
    mocked_response.status_code = 200
    mocked_response.text = "OK"
    return mocked_response


def patched_request_get_500(url: str) -> requests.Response:
    mocked_response.status_code = 500
    mocked_response.text = "Server Error"
    return mocked_response


def patched_os_path_exists(filename) -> bool:
    return True


def patched_storage_load_file_contents(self, filename: str) -> None:
    # return what is needed in each moment

    return STORAGE_PER_FILENAME[filename]


@patch.object(Config, "read_file", new=patched_config_read_file)
@patch.object(Logger, "__init__", new=patched_logger_init)
@patch.object(Logger, "get_logger", new=patched_logger_get_logger)
def instantiate_dependencies() -> tuple:
    # Prepare injected objects
    config = Config()
    logger = Logger(config).get_logger()

    return (config, logger)


@patch.object(Storage, "_load_file_contents", new=patched_storage_load_file_contents)
@patch.object(os.path, "exists", new=patched_os_path_exists)
def get_instance() -> UpdateDdns:
    config, logger = instantiate_dependencies()

    instance = UpdateDdns(config=config, logger=logger)

    # The library instantiates the logger itself
    assert instance._logger == instance._directnic._logger

    return instance


def test_init():

    instance = get_instance()

    # The library instantiates the logger itself
    assert instance._logger == instance._directnic._logger


@patch.object(Network, "get_external_ipv4", new=patched_network_get_external_ip)
@patch.object(requests, "get", new=patched_request_get_200)
def test_ips_are_different_update_ok():

    instance = get_instance()

    mocked_do_status_publish = Mock()
    mocked_write_file = Mock()
    with patch.object(instance._service_publisher,
                      "_do_status_publish",
                      new=mocked_do_status_publish):
        with patch.object(instance._directnic._storage, "write_file", new=mocked_write_file):
            instance.run()

    mocked_do_status_publish.assert_called_once()
    assert instance._directnic._storage.get("last_external_ip") == EXTERNAL_IP
    mocked_write_file.assert_called_once()


@patch.object(Network, "get_external_ipv4", new=patched_network_get_external_ip)
def test_ips_are_same():
    STORAGE_PER_FILENAME[f"{ROOT_DIR}/storage/external_ip.yaml"]["last_external_ip"
                                                                 ] = EXTERNAL_IP

    instance = get_instance()

    mocked_logger_info = Mock()
    mocked_do_status_publish = Mock()
    mocked_write_file = Mock()
    with patch.object(instance._logger, "info", new=mocked_logger_info):
        with patch.object(instance._service_publisher,
                          "_do_status_publish",
                          new=mocked_do_status_publish):
            with patch.object(instance._directnic._storage, "write_file",
                              new=mocked_write_file):
                instance.run()

    # Nothing is done, just a log annotate
    mocked_do_status_publish.assert_not_called()
    mocked_write_file.assert_not_called()
    mocked_logger_info.assert_called_with(
        "Current external IP is the same as the previous known."
    )
