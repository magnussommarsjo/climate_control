from controller.storage import QueryBuilder


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
