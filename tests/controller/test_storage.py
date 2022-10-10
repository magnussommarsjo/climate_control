from controller.storage import InfluxStorage, QueryBuilder
import pytest
import os


@pytest.fixture
def influxdb():
    start_infuxdb_cmd = """
    docker run -d -p 8087:8086 \
    -e DOCKER_INFLUXDB_INIT_MODE=setup \
    -e DOCKER_INFLUXDB_INIT_USERNAME=admin \
    -e DOCKER_INFLUXDB_INIT_PASSWORD=password \
    -e DOCKER_INFLUXDB_INIT_ORG=org \
    -e DOCKER_INFLUXDB_INIT_BUCKET=bucket \
    -e DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=my-super-secret-auth-token \
    --name pytest_influxdb \
    influxdb:2.4
    """

    remove_influxdb_cmd = """
    docker stop pytest_influxdb
    """

    os.system(start_infuxdb_cmd)
    # TODO: How to wait for docker container to be fully ready?
    yield None
    os.system(remove_influxdb_cmd)


def test_influxdb():
    influx_storage = InfluxStorage(
        address="localhost",
        port=8087,
        token="my-super-secret-auth-token",
        org="org",
        bucket="bucket",
    )

    data_to_write = {
        "test_sensor_1": {"attribute_1": 101, "attribute_2": 102},
        "test_sensor_2": {"attribute_1": 201, "attribute_2": 202},
    }

    influx_storage.store(
        measurement="Test",
        data=data_to_write,
        tags=[("location", "home"), ("type", "test")],
    )


def test_query_builder():
    qb = QueryBuilder()
    qb = (
        qb.bucket("bucket")
        .range("-1h", "-10m")
        .measurement("Test")
        .filter("location", "home")
        )
    assert qb.build() == (
    'from(bucket: "bucket")\n'
    '  |> range(start: -1h, stop: -10m)\n'
    '  |> filter(fn: (r) => r["_measurement"] == "Test")\n'
    '  |> filter(fn: (r) => r["location"] == "home")\n'
    '  |> yield()'
    )
