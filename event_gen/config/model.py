import logging
from pathlib import Path
from typing import Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, model_validator

LOG = logging.getLogger(__name__)
T_VALUE = Union[int, float]
DIST_SEP = ":"


class NullValue:
    pass


class _NullInt(NullValue, int):
    pass


class _NullString(NullValue, str):
    pass


NULL_INT = _NullInt(0)
NULL_STR = _NullString("")


class DistributionTypes(Enum):
    Linear = "linear"
    StdDev = "stdDev"


class Progress(Enum):
    Trend = "trend"
    Last = "last"


class ValueRange(BaseModel):
    min: T_VALUE
    max: T_VALUE
    distribution: DistributionTypes = DistributionTypes.Linear
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


class PropertyConfig(BaseModel):
    start: Union[str, int, float]
    trend: Optional[str] = None
    progression: Optional[Progress] = Progress.Trend
    value_range: Optional[ValueRange] = None
    conditions: list[str] = Field(default_factory=list)


class ModuleConfig(BaseModel):
    max_generator_retries: int = Field(default=NULL_INT, gt=0)
    max_historian_buffer: int = Field(default=NULL_INT, gt=0)


class ObjectConfig(BaseModel):
    schema: str | Path
    properties: dict[str, PropertyConfig]

    @model_validator(mode="after")
    def load_schema(self):
        if isinstance(self.schema, str):
            self.schema = Path(self.schema)
        return self


class ProjectConfig(BaseModel):
    config: Optional[ModuleConfig] = None
    objects: dict[str, ObjectConfig]
    _base_path: Path = None
