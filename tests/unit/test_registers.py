import pytest

from husdata import registers as reg


@pytest.mark.parametrize(
    "idx,data_type",
    [
        ("0002", reg.DataType.DEGREES),
        ("1A01", reg.DataType.ON_OFF_BOOL),
        ("B20A", reg.DataType.NUMBER),
        ("2204", reg.DataType.NUMBER),
        ("3104", reg.DataType.PERCENT),
        ("6209", reg.DataType.HOURS),
        ("5C52", reg.DataType.KWH),
    ]
)
def test_is_data_type(idx: str, data_type: reg.DataType):
    assert reg.is_data_type(idx, data_type)