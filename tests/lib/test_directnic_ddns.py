from pyxavi.config import Config
from pyxavi.storage import Storage
from pyxavi.network import Network
from janitor.lib.directnic_ddns import DirectnicDdns
from unittest.mock import patch, Mock
from logging import Logger
import requests

CONFIG = {"logger.name": "logger_test", "directnic_ddns.file": "storage/external_ip.yaml"}


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


def get_instance() -> DirectnicDdns:
    with patch.object(Config, "__init__", new=patched_config_init):
        with patch.object(Config, "get", new=patched_config_get):
            with patch.object(Storage, "__init__", new=patched_storage_init):
                return DirectnicDdns(config=Config())


def test_initialize():
    updater = get_instance()

    assert isinstance(updater, DirectnicDdns)
    assert isinstance(updater._config, Config)
    assert isinstance(updater._logger, Logger)
    assert isinstance(updater._storage, Storage)


def test_get_external_ip_first_time():
    test_address = "1.1.1.1"

    updater = get_instance()

    assert updater.current_external_ip is None

    mocked_get_ip = Mock()
    mocked_get_ip.return_value = test_address
    with patch.object(Network, "get_external_ipv4", new=mocked_get_ip):
        external_ip = updater.get_external_ip()

        mocked_get_ip.assert_called_once()
        assert external_ip == test_address
        assert updater.current_external_ip == test_address


def test_get_external_ip_second_time():
    test_address = "1.1.1.1"

    updater = get_instance()
    updater.current_external_ip = test_address

    mocked_get_ip = Mock()
    with patch.object(Network, "get_external_ipv4", new=mocked_get_ip):
        external_ip = updater.get_external_ip()

        mocked_get_ip.assert_not_called()
        assert external_ip == test_address
        assert updater.current_external_ip == test_address


def test_current_ip_is_different_yes():
    test_address = "1.1.1.1"
    previous_address = "2.2.2.2"

    updater = get_instance()

    mocked_storage_get = Mock()
    mocked_storage_get.return_value = previous_address
    mocked_get_ip = Mock()
    mocked_get_ip.return_value = test_address
    with patch.object(updater._storage, "get", new=mocked_storage_get):
        with patch.object(updater, "get_external_ip", new=mocked_get_ip):

            result = updater.current_ip_is_different()
            assert result is True


def test_current_ip_is_different_no():
    test_address = "1.1.1.1"
    previous_address = "1.1.1.1"

    updater = get_instance()

    mocked_storage_get = Mock()
    mocked_storage_get.return_value = previous_address
    mocked_get_ip = Mock()
    mocked_get_ip.return_value = test_address
    with patch.object(updater._storage, "get", new=mocked_storage_get):
        with patch.object(updater, "get_external_ip", new=mocked_get_ip):

            result = updater.current_ip_is_different()
            assert result is False


def test_build_updating_link():
    test_address = "1.1.1.1"
    link = "http://abc.de"

    updater = get_instance()

    mocked_get_ip = Mock()
    mocked_get_ip.return_value = test_address
    with patch.object(updater, "get_external_ip", new=mocked_get_ip):
        result = updater.build_updating_link(link)
        assert result == f"{link}{test_address}"


def test_send_update_ok():
    url = "http://abc.de?ip=1.1.1.1"

    updater = get_instance()

    class Response:
        status_code: int
        text: str
        reason: str

        def __init__(self, status_code: int, text: str = None, reason: str = None) -> None:
            self.status_code = status_code
            self.text = text
            self.reason = reason

    mocked_requests_request = Mock()
    mocked_requests_request.return_value = Response(status_code=200, text="OK")
    with patch.object(requests, "get", new=mocked_requests_request):
        result = updater.send_update(updating_url=url)

        assert result is True


def test_send_update_ko():
    url = "http://abc.de?ip=1.1.1.1"

    updater = get_instance()

    class Response:
        status_code: int
        text: str
        reason: str

        def __init__(self, status_code: int, text: str = None, reason: str = None) -> None:
            self.status_code = status_code
            self.text = text
            self.reason = reason

    mocked_requests_request = Mock()
    mocked_requests_request.return_value = Response(status_code=429, text="KO")
    with patch.object(requests, "get", new=mocked_requests_request):
        result = updater.send_update(updating_url=url)

        assert result is False


def test_save_current_ip():
    test_address = "1.1.1.1"

    updater = get_instance()

    mocked_storage_set = Mock()
    mocked_storage_write = Mock()
    mocked_get_ip = Mock()
    mocked_get_ip.return_value = test_address
    with patch.object(updater._storage, "set", new=mocked_storage_set):
        with patch.object(updater._storage, "write_file", new=mocked_storage_write):
            with patch.object(updater, "get_external_ip", new=mocked_get_ip):

                _ = updater.save_current_ip()

                mocked_storage_set.assert_called_once_with("last_external_ip", test_address)
                mocked_storage_write.assert_called_once()
