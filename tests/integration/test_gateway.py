import pytest

from husdata.gateway import H60
from controller import config as cfg

@pytest.fixture(scope='session')
def config() -> cfg.Config:
    """Get configurations/environment vraiables"""
    return cfg.read_config()


@pytest.fixture
def h60(config: cfg.Config) -> H60:
    """H60 fixture with environments"""
    h60 = H60(
        address= config.H60_ADDRESS
    )
    return h60


@pytest.mark.parametrize("do_convert", [True, False])
def test_get_all_data(do_convert: bool, h60: H60):
    """Get all data with and without convert"""
    data = h60.get_all_data(convert=do_convert)

    assert data # Non empty dict
