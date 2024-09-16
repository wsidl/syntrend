import datetime
import random
import re
import logging
from typing import Union, TYPE_CHECKING
import math

if TYPE_CHECKING:
    from syntrend.utils.manager import SeriesManager

LOG = logging.getLogger(__name__)
R_DATETIME = re.compile(r'[1-2]\d{3}-[0-1]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d')
R_TIME = re.compile(r'[0-2]\d:[0-5]\d:[0-5]\d')
R_DATE = re.compile(r'[1-2]\d{3}-[0-1]\d-[0-3]\d')
R_DELTA = re.compile(r'(\d+)([dHMS])')
DELTA_ABBR_MAP = {'d': 'days', 'H': 'hours', 'M': 'minutes', 'S': 'seconds'}

MANAGER: Union['SeriesManager', None] = None


def to_timestamp(value: datetime.datetime):
    return value.timestamp()


def to_datetime(value_string, format_str: str = None):
    for formatter in [datetime.datetime.fromisoformat, datetime.date.fromisoformat, datetime.time.fromisoformat]:
        try:
            return formatter(value_string)
        except (TypeError, ValueError) as e:
            print(e)
            pass
    if format_str is not None:
        try:
            return datetime.datetime.strptime(value_string, format_str)
        except ValueError:
            pass
    time_parts = {}
    for match in R_DELTA.finditer(value_string):
        time_parts[DELTA_ABBR_MAP[match.group(2)]] = int(match.group(1))
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


def get_object(object_name):
    historian = MANAGER.historians[object_name]
    generator = MANAGER.generators[object_name]

    def get_index(index: int = 0):
        if index == 0:
            return generator
        if index <= len(historian):
            return historian[index - 1]
        return None

    return get_index


def load_environment(manager: 'SeriesManager'):
    global MANAGER
    MANAGER = manager
    manager.expression_env.globals.update(
        datetime=datetime.datetime,
        timedelta=datetime.timedelta,
        time=datetime.time,
        date=datetime.date,
        sin=math.sin,
        cos=math.cos,
        tan=math.tan,
        degrees=math.degrees,
        radians=math.radians,
        random=random.random,
        pi=math.pi,
    )
    manager.expression_env.filters.update(
        to_timestamp=to_timestamp,
        to_datetime=to_datetime,
        series=series,
        # path=get_path,
    )
    for object_name in manager.historians:
        manager.expression_env.globals[object_name] = get_object(object_name)
