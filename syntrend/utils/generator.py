from syntrend.config import model
from syntrend.generators import historian, filters

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


# class ValueRange(BaseModel):
#     min: T_VALUE
#     max: T_VALUE
#     distribution: model.DistributionTypes = model.DistributionTypes.Linear
#     factor: float = Field(0.0)
#
#     def __init__(self, **kwargs):
#         if (
#             "distribution" in kwargs
#             and isinstance(kwargs["distribution"], str)
#             and "factor" not in kwargs
#             and DIST_SEP in kwargs["distribution"]
#         ):
#             parts = kwargs["distribution"].split(DIST_SEP)
#             kwargs["factor"] = parts[1]
#             kwargs["distribution"] = parts[0]
#         super().__init__(**kwargs)
#
#
# SeriesConfig = ForwardRef("SeriesConfig")
# T_NegInt = Annotated[int, Le(0)]


# class PropertyGenerator:
#     def __init__(self, property_config: model.PropertyDefinition):
#         self.config = property_config
#         self.__series = None
#         self.__trend_env = Environment(loader=BaseLoader())
#         self.__condition_env = Environment(loader=BaseLoader())
#         filters.load_environment(self.__trend_env)
#         filters.load_environment(self.__condition_env)
#         self.__generator: callable = None
#         self.__trend_historian = historian.Historian()
#         self.__condition_historian = historian.Historian()
#         self.__conditions: list[TemplateExpression] = []
#         self.__trend_calc: callable = None
#         self.init(None)
#
#     @property
#     def trend_historian(self):
#         return (
#             self.__trend_historian
#             if self.config.progression == model.Progress.Trend
#             else self.__condition_historian
#         )
#
#     @property
#     def condition_historian(self):
#         return self.__condition_historian
#
#     def init(self, series: SeriesConfig):
#         self.__series = series
#         if isinstance(self.config.start, str):
#             self.config.start = self.__trend_env.from_string(self.config.start).render()
#         self.trend_historian.clear()
#         self.condition_historian.clear()
#         filters.load_environment(self.__trend_env)
#         filters.load_environment(self.__condition_env)
#         self.__trend_env.globals["this"] = self.trend_historian
#         self.__condition_env.globals["this"] = self.condition_historian
#         if self.__series:
#             for obj_name in self.__series.objects:
#                 for prop_gen in self.__series.objects[obj_name].properties:
#                     self.__trend_env.globals[prop_gen] = self.__series.objects[obj_name].properties[
#                         prop_gen
#                     ].trend_historian
#                     self.__condition_env.globals[prop_gen] = self.__series.objects[obj_name].properties[
#                         prop_gen
#                     ].condition_historian
#         self.__generator = generator_factory(self.config.value_range)
#         self.__conditions = [
#             self.__condition_env.compile_expression(c) for c in self.config.conditions
#         ]
#         if not self.config.trend:
#             self.__trend_calc = lambda: self.config.start
#         else:
#             self.__trend_calc = self.__trend_env.compile_expression(self.config.trend)
#
#     def generate(self) -> T_VALUE:
#         condition_state = False
#         new_value = None
#         retries = []
#         while not condition_state:
#             seed_value = (
#                 self.__trend_calc() if self.trend_historian.has_values() else self.config.start
#             )
#             new_value = (
#                 self.__generator(seed_value)
#                 if self.trend_historian.has_values()
#                 else self.config.start
#             )
#             self.trend_historian.append(seed_value)
#             self.condition_historian.append(new_value)
#             LOG.debug("%s, %s", str(seed_value), str(new_value))
#             condition_state = all([cond() for cond in self.__conditions])
#             if not condition_state:
#                 retries.append(new_value)
#                 self.trend_historian.pop(-1)
#                 self.condition_historian.pop(-1)
#                 if len(retries) == MAX_GENERATOR_RETRIES:
#                     raise ValueError(
#                         "Generator cannot provide a value that also meets condition requirements. "
#                         "Try adjusting conditions, range, or trend parameters.\n"
#                         f"Generated values attempted: [{', '.join([str(v) for v in retries])}]"
#                     )
#                 LOG.debug(f"Conditions failed with {new_value}, trying again")
#         return new_value
