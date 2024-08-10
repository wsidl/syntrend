from syntrend.generators import register, PropertyGenerator

from datetime import datetime, timedelta, timezone
from time import localtime
from functools import partial
import re

RE_TIME_OFFSET = re.compile(r"(-?\d+)([YmdHMS])")
DATETIME_SYMBOL_MAP = {
    "Y": "years",
    "m": "months",
    "d": "days",
    "H": "hours",
    "M": "minutes",
    "S": "seconds",
}


def datetime_aware(kwargs):
    kwargs["is_utc"] = bool(kwargs.get("is_utc", True))
    kwargs["tz_offset"] = timezone(timedelta(seconds=0 if kwargs["is_utc"] else localtime().tm_gmtoff))

    def generator(self):
        return self.kwargs.now().astimezone(self.kwargs.tz_offset)

    kwargs["generate"] = generator
    kwargs["now"] = partial(datetime.now, tz=timezone.utc)


@register
class DateTimeGenerator(PropertyGenerator):
    type = str
    name = "datetime"
    default_config = {
        "format": "%Y-%m-%dT%H:%M:%S%z",
        "is_utc": True,
        "time_offset": "0d",
    }

    def load_kwargs(self, kwargs: dict[str, any]) -> dict[str, any]:
        offset_matches = {}
        for _match in RE_TIME_OFFSET.finditer(kwargs["time_offset"]):
            val, key = _match.groups()
            offset_matches[DATETIME_SYMBOL_MAP[key]] = int(val)
        kwargs["time_offset"] = timedelta(**offset_matches)
        datetime_aware(kwargs)
        return kwargs

    def generate(self):
        return (self.kwargs.generate(self) + self.kwargs.time_offset).strftime(self.kwargs.format)


@register
class TimestampGenerator(PropertyGenerator):
    type = int
    name = "timestamp"
    default_config = {
        "time_offset": 0,
    }

    def load_kwargs(self, kwargs: dict[str, any]) -> dict[str, any]:
        datetime_aware(kwargs)
        kwargs["time_offset"] = int(kwargs["time_offset"])
        return kwargs

    def generate(self):
        return int(self.kwargs.generate(self).timestamp()) + self.kwargs.time_offset
