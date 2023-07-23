import pytest
from datetime import date
from common.utils import (
    serialize_objects_to_single_json,
    deserialize_single_json_to_objects,
    get_date_parts_from_date,
    get_object_key,
    estimate_downvotes,
)


@pytest.mark.parametrize(
    "objects, expected_json",
    [
        (
            [],
            "[]"
        ),
        (
            [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
            '[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]'
        ),
    ],
)
def test_serialize_objects_to_single_json(objects, expected_json):
    result_json = serialize_objects_to_single_json(objects)
    assert result_json == expected_json


@pytest.mark.parametrize(
    "json_string, model_type, expected_objects",
    [
        (
            '[]',
            dict,
            []
        ),
        (
            '[{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]',
            dict,
            [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
        ),
    ],
)
def test_deserialize_single_json_to_objects(json_string, model_type, expected_objects):
    result_objects = deserialize_single_json_to_objects(json_string, model_type)
    assert result_objects == expected_objects


@pytest.mark.parametrize(
    "date_input, expected_parts",
    [
        (date(2023, 7, 1), ("2023", "07", "01")),
        (date(2000, 1, 1), ("2000", "01", "01")),
    ],
)
def test_get_date_parts_from_date(date_input, expected_parts):
    result_parts = get_date_parts_from_date(date_input)
    assert result_parts == expected_parts


@pytest.mark.parametrize(
    "prefix, date_input, expected_key",
    [
        ("prefix", date(2023, 7, 1), "prefix/year=2023/month=07/day=01.json"),
        ("my-data", date(2020, 12, 25), "my-data/year=2020/month=12/day=25.json"),
    ],
)
def test_get_object_key(prefix, date_input, expected_key):
    result_key = get_object_key(prefix, date_input)
    assert result_key == expected_key


@pytest.mark.parametrize(
    "upvotes, upvote_ratio, expected_downvotes",
    [
        (100, 0.5, 100),
        (50, 0.0, 0),
    ],
)
def test_estimate_downvotes(upvotes, upvote_ratio, expected_downvotes):
    result_downvotes = estimate_downvotes(upvotes, upvote_ratio)
    assert result_downvotes == expected_downvotes
