import importlib
import sys


def test_config_read(mocker):
    mocker.patch("tomllib.load", return_value={"test": "test"})
    from server import config

    importlib.reload(sys.modules["server.config"])

    assert config.test == "test"


def test_config_mock(mock_config):
    from server import config

    assert config.im["app_id"] == "123456"
    assert config.im["secret_key"] == "123456"
    assert config.im["admin"] == "admin"
