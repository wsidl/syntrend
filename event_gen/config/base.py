import datetime
import re
import logging
import json
import yaml
from yaml.parser import ParserError
from pathlib import Path

from jinja2 import Environment

LOG = logging.getLogger(__name__)
R_DATETIME = re.compile(r"[1-2]\d{3}-[0-1]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d")
R_TIME = re.compile(r"[0-2]\d:[0-5]\d:[0-5]\d")
R_DATE = re.compile(r"[1-2]\d{3}-[0-1]\d-[0-3]\d")
R_DELTA = re.compile(r"(\d+)([dhms])")
DELTA_ABBR_MAP = {"d": "days", "h": "hours", "m": "minutes", "s": "seconds"}


def to_timestamp(value: datetime.datetime):
    return value.timestamp()


def to_datetime(value_string):
    try:
        return datetime.datetime.fromisoformat(value_string)
    except ValueError:
        pass
    try:
        return datetime.date.fromisoformat(value_string)
    except ValueError:
        pass
    try:
        return datetime.time.fromisoformat(value_string)
    except ValueError:
        pass
    time_parts = {}
    for match in R_DELTA.finditer(value_string):
        time_parts[DELTA_ABBR_MAP[match.group(2)]] = match.group(1)
    return datetime.timedelta(**time_parts)


def series(generator, series_length):
    class _Comparator:
        def __init__(self):
            self._v = [
                generator.condition_historian(i) for i in range(0, -series_length, -1)
            ]

        def __eq__(self, other):
            return all([a == other for a in self._v])

        def __ne__(self, other):
            return all([a != other for a in self._v])

        def __gt__(self, other):
            return all([a > other for a in self._v])

        def __ge__(self, other):
            return all([a >= other for a in self._v])

        def __lt__(self, other):
            return all([a < other for a in self._v])

        def __le__(self, other):
            return all([a <= other for a in self._v])

        def __contains__(self, item):
            return item in self._v

    return _Comparator()


def load_environment(env: Environment):
    env.globals.update(
        datetime=datetime.datetime,
        timedelta=datetime.timedelta,
        time=datetime.time,
        date=datetime.date,
    )
    env.filters["to_timestamp"] = to_timestamp
    env.filters["to_datetime"] = to_datetime
    env.filters["series"] = series





