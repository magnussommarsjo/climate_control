import pytest
from unittest.mock import MagicMock

from husdata.gateway import H60
from controller import config as cfg

@pytest.fixture(scope='session')
def config() -> cfg.Config:
    """Get configurations/environment variables"""
    return cfg.read_config(
        SAMPLE_TIME = 60,
        HOST = "0.0.0.0",
        PORT = 80,
        H60_ADDRESS = "",
        MQTT_HOST = "",
        MQTT_PORT = 1883,
        MQTT_CLIENT_ID = "test"
    )


@pytest.fixture
def h60(config: cfg.Config) -> H60:
    """H60 fixture with environments"""
    mock_mqtt_client = MagicMock()
    h60 = H60(client=mock_mqtt_client)
    h60.raw_data = {
        "dummy": "data"
    }
    return h60


@pytest.mark.parametrize("do_convert", [True, False])
def test_get_all_data(do_convert: bool, h60: H60):
    """Get all data with and without convert"""
    data = h60.get_all_data(convert=do_convert)

    assert data # Non empty dict
