from syntrend.generators import register, PropertyGenerator

from datetime import datetime, timedelta
import re

RE_TIME_OFFSET = re.compile(r"(\d+)([YmdHMS])")
DATETIME_SYMBOL_MAP = {
    "Y": "years",
    "m": "months",
    "d": "days",
    "H": "hours",
    "M": "minutes",
    "S": "seconds",
}


@register
class DateTimeGenerator(PropertyGenerator):
    name = "datetime"
    default_config = {
        "format": "%Y-%m-%dT%H:%M:%S%z",
        "is_utc": True,
        "time_offset": "0d",
    }

    def load_kwargs(self, kwargs: dict[str, any]) -> dict[str, any]:
        kwargs["is_utc"] = bool(kwargs["is_utc"])

        offset_matches = {}
        for _match in RE_TIME_OFFSET.finditer(kwargs["time_offset"]):
            val, key = _match.groups()
            offset_matches[DATETIME_SYMBOL_MAP[key]] = int(val)
        kwargs["time_offset"] = timedelta(**offset_matches)
        kwargs["now"] = datetime.utcnow if kwargs["is_utc"] else datetime.now
        return kwargs

    def generate(self):
        return self.kwargs.now() + self.kwargs.time_offset


@register
class TimestampGenerator(PropertyGenerator):
    name = "timestamp"
    default_config = {
        "is_utc": True,
        "time_offset": 0,
    }

    def load_kwargs(self, kwargs: dict[str, any]) -> dict[str, any]:
        kwargs["is_utc"] = bool(kwargs["is_utc"])
        kwargs["time_offset"] = int(kwargs["time_offset"])
        kwargs["now"] = lambda: (datetime.utcnow if kwargs["is_utc"] else datetime.now)().timestamp()
        return kwargs

    def generate(self):
        return int(self.kwargs.now()) + self.kwargs.time_offset
