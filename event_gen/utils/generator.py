from event_gen.config.base import load_environment
from event_gen.config import model

from random import uniform, betavariate
from enum import Enum
from typing import Union, Optional, ForwardRef, Any, Annotated
from annotated_types import Le
import logging

from pydantic import BaseModel, Field
from jinja2 import Environment, BaseLoader
from jinja2.environment import TemplateExpression

LOG = logging.getLogger(__name__)
T_VALUE = Union[int, float]
T_ALL_VALUE = Union[T_VALUE, str]
DIST_SEP = ":"
MAX_HISTORIAN_BUFFER = 20
MAX_GENERATOR_RETRIES = 20


def generator_factory(value_range: "model.ValueRange"):
    if not value_range:
        def simple(new_value: T_ALL_VALUE) -> T_ALL_VALUE:
            return new_value

        return simple

    if value_range.distribution == model.DistributionTypes.Linear:
        def linear_calc(new_value: T_VALUE) -> T_VALUE:
            return uniform(
                value_range.min + float(new_value), value_range.max + float(new_value)
            )

        return linear_calc

    if value_range.distribution == model.DistributionTypes.StdDev:
        scale = value_range.max - value_range.min
        unscaled_var = (float(value_range.factor) / scale) ** 2
        unscaled_mean = -value_range.min / scale
        t = unscaled_mean / (1 - unscaled_mean)
        beta = ((t / unscaled_var) - (t * t) - (2 * t) - 1) / (
            (t * t * t) + (3 * t * t) + (3 * t) + 1
        )
        alpha = beta * t
        if alpha <= 0 or beta <= 0:
            raise ValueError("Cannot create value in Std Dev with given numbers")

        def stddev_calc(new_value: T_VALUE) -> T_VALUE:
            return betavariate(alpha, beta) * scale + value_range.min + float(new_value)

        return stddev_calc

    raise ValueError(
        f"Unsupported value provided for distribution type: {value_range.distribution}"
    )


class ValueRange(BaseModel):
    min: T_VALUE
    max: T_VALUE
    distribution: model.DistributionTypes = model.DistributionTypes.Linear
    factor: float = Field(0.0)

    def __init__(self, **kwargs):
        if (
            "distribution" in kwargs
            and isinstance(kwargs["distribution"], str)
            and "factor" not in kwargs
            and DIST_SEP in kwargs["distribution"]
        ):
            parts = kwargs["distribution"].split(DIST_SEP)
            kwargs["factor"] = parts[1]
            kwargs["distribution"] = parts[0]
        super().__init__(**kwargs)


SeriesConfig = ForwardRef("SeriesConfig")
T_NegInt = Annotated[int, Le(0)]


class Historian(list):
    def __init__(self):
        super().__init__()
        self.clear()

    # Historian Manager methods
    def __get_value(self, item: T_NegInt = 0):
        offset = item - 1
        list_size = super().__len__()
        if list_size == 0:
            raise ValueError("No values added to historian")
        if -offset <= list_size:
            return super().__getitem__(offset)
        return super().__getitem__(0)

    def __getitem__(self, item: T_NegInt) -> Union[str, int, float]:
        return self.__get_value(item)

    def __call__(self, item: T_NegInt = 0):
        return self.__get_value(item)

    def append(self, _object):
        super().append(_object)
        while super().__len__() > MAX_HISTORIAN_BUFFER:
            super().pop(0)

    def has_values(self) -> bool:
        return super().__len__() > 0

    ##########################################################
    # Convenience Operators when defaulting to current value #
    ##########################################################
    @property
    def current(self):
        return super().__getitem__(-1)

    # Comparator Methods
    def __eq__(self, other):
        return self.current == other

    def __ne__(self, other):
        return self.current != other

    def __lt__(self, other):
        return self.current < other

    def __le__(self, other):
        return self.current <= other

    def __gt__(self, other):
        return self.current > other

    def __ge__(self, other):
        return self.current >= other

    # Arithmetic Operators
    def __add__(self, other):
        return self.current + other

    def __sub__(self, other):
        return self.current - other

    def __mul__(self, other):
        return self.current * other

    # Formatting / Type Casting
    def __len__(self):
        return super().__len__()

    def __int__(self):
        return int(self.current)

    def __float__(self):
        return float(self.current)

    def __hex__(self):
        current = self.current
        if isinstance(current, int):
            return hex(current)
        if isinstance(current, float):
            return current.hex()
        raise TypeError("Value in this series cannot be converted to Hexadecimal")

    def __format__(self, format_spec):
        return format(self.current, format_spec)

    def __str__(self):
        return str(self.current)

    def __repr__(self):
        return str(self.current)

    # Removing unwanted methods
    def insert(self, _, __):
        raise AttributeError("'Historian' object has no attribute 'insert'")

    def __iter__(self):
        raise AttributeError("'Historian' object has no attribute '__iter__'")

    def __next__(self):
        raise AttributeError("'Historian' object has no attribute '__next__'")

    def __contains__(self, item):
        raise AttributeError("'Historian' object has no attribute '__contains__'")


class PropertyGenerator:
    def __init__(self, property_config: model.PropertyConfig):
        self.config = property_config
        self.__series = None
        self.__trend_env = Environment(loader=BaseLoader())
        self.__condition_env = Environment(loader=BaseLoader())
        load_environment(self.__trend_env)
        load_environment(self.__condition_env)
        self.__generator: callable = None
        self.__trend_historian = Historian()
        self.__condition_historian = Historian()
        self.__conditions: list[TemplateExpression] = []
        self.__trend_calc: callable = None
        self.init(None)

    @property
    def trend_historian(self):
        return (
            self.__trend_historian
            if self.config.progression == model.Progress.Trend
            else self.__condition_historian
        )

    @property
    def condition_historian(self):
        return self.__condition_historian

    def init(self, series: SeriesConfig):
        self.__series = series
        if isinstance(self.config.start, str):
            self.config.start = self.__trend_env.from_string(self.config.start).render()
        self.trend_historian.clear()
        self.condition_historian.clear()
        load_environment(self.__trend_env)
        load_environment(self.__condition_env)
        self.__trend_env.globals["this"] = self.trend_historian
        self.__condition_env.globals["this"] = self.condition_historian
        if self.__series:
            for obj_name in self.__series.objects:
                for prop_gen in self.__series.objects[obj_name].properties:
                    self.__trend_env.globals[prop_gen] = self.__series.objects[obj_name].properties[
                        prop_gen
                    ].trend_historian
                    self.__condition_env.globals[prop_gen] = self.__series.objects[obj_name].properties[
                        prop_gen
                    ].condition_historian
        self.__generator = generator_factory(self.config.value_range)
        self.__conditions = [
            self.__condition_env.compile_expression(c) for c in self.config.conditions
        ]
        if not self.config.trend:
            self.__trend_calc = lambda: self.config.start
        else:
            self.__trend_calc = self.__trend_env.compile_expression(self.config.trend)

    def generate(self) -> T_VALUE:
        condition_state = False
        new_value = None
        retries = []
        while not condition_state:
            seed_value = (
                self.__trend_calc() if self.trend_historian.has_values() else self.config.start
            )
            new_value = (
                self.__generator(seed_value)
                if self.trend_historian.has_values()
                else self.config.start
            )
            self.trend_historian.append(seed_value)
            self.condition_historian.append(new_value)
            LOG.debug("%s, %s", str(seed_value), str(new_value))
            condition_state = all([cond() for cond in self.__conditions])
            if not condition_state:
                retries.append(new_value)
                self.trend_historian.pop(-1)
                self.condition_historian.pop(-1)
                if len(retries) == MAX_GENERATOR_RETRIES:
                    raise ValueError(
                        "Generator cannot provide a value that also meets condition requirements. "
                        "Try adjusting conditions, range, or trend parameters.\n"
                        f"Generated values attempted: [{', '.join([str(v) for v in retries])}]"
                    )
                LOG.debug(f"Conditions failed with {new_value}, trying again")
        return new_value
