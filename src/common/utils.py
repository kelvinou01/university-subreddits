from __future__ import annotations

import json
from datetime import date as Date
from datetime import datetime
from datetime import timedelta
from typing import List

from common.models import AbstractModel


def serialize_objects_to_single_json(
    objects: List[AbstractModel],
) -> str:
    list_of_object_dicts = [dict(object) for object in objects]
    return json.dumps(list_of_object_dicts, default=str)


def deserialize_single_json_to_objects(
    json_string: str,
    model_type: type[AbstractModel],
) -> list[AbstractModel]:
    list_of_object_dicts = json.loads(json_string)
    return [model_type(**object_dict) for object_dict in list_of_object_dicts]


def get_date_parts_from_date(date: Date) -> tuple[str, str, str]:
    """
    Helper function to get different parts of a date as double-digit strings
    """
    year = f"{date.year}"
    month = f"{date.month:02d}"
    day = f"{date.day:02d}"
    return year, month, day


def get_object_key(date: Date) -> str:
    """
    Assuming partitioning by year+month, using the hour as the object name and saving in json format:
    the method returns a cloud storage object key based on a prefix and a datetime object.
    """
    year, month, day = get_date_parts_from_date(date)
    partition_prefix = f"year={year}/month={month}"
    object_name = f"day={day}.json"

    return f"{partition_prefix}/{object_name}"


def get_date(object_key: str) -> Date:
    year_str, month_str, day_str = object_key.split("/")
    year = int(year_str[5:9])
    month = int(month_str[6:11])
    day = int(day_str[4:6])
    return datetime(year, month, day).date()


def estimate_downvotes(upvotes: int, upvote_ratio: float) -> int:
    """
    Estimates the number of downvotes based on the number of upvotes and the upvote ratio
    """
    if upvote_ratio < 0:
        raise ValueError("upvote_ratio cannot be negative")
    elif upvote_ratio == 0.0:
        estimated_downvotes = 0.0
    else:
        # rearranged: upvote_ratio = upvotes / (upvotes + downvotes)
        estimated_downvotes = upvotes / upvote_ratio - upvotes
    return int(round(estimated_downvotes))


def get_default_date_for_extract_call():
    default_date = datetime.today() - timedelta(days=1)
    return default_date.date()
