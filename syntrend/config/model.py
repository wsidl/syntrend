"""Project File Schema"""

import logging
from typing import Union, Optional
import dataclasses as dc
from enum import Enum
from os import getenv
from pathlib import Path
from functools import partial

LOG = logging.getLogger(__name__)
DEFAULT_ENVVAR_PREFIX = "SYNTREND_"
OUTPUT_STDOUT = Path("-")
DEFAULT_FILE_FORMAT = "{name}-{id}.{format}"
USER_CONFIG_DIR = Path.home().joinpath(".config", "syntrend")
ADD_GENERATOR_DIR = USER_CONFIG_DIR.joinpath("generators")

dataclass = partial(dc.dataclass, kw_only=True, init=False)


class NullValue:
    pass


class _NullInt(NullValue, int):
    pass


class _NullString(NullValue, str):
    pass


NULL_VAL = NullValue()
NULL_INT = _NullInt(0)
NULL_STR = _NullString("")


class DistributionTypes(Enum):
    NoDistribution = "none"
    Linear = "linear"
    StdDev = "stdDev"


class Progress(Enum):
    Trend = "trend"
    Last = "last"


class SeriesType(Enum):
    Sequence = "sequence"
    Reference = "reference"


def fields(obj: dc.dataclass, include_field=False) -> list[str|dc.Field]:
    return [field if include_field else field.name for field in dc.fields(obj)]


@dataclass
class Validated:
    """Base Class for Configurations"""
    source__: dict = dc.field(default_factory=dict)

    def __init__(self, **kwargs):
        """Runs Parsing methods (if declared) to parse dataclass fields and validation method. Requires
        a method to match the field name with the following signature:
          `parse_<field.name>(self, value) -> any`
        """
        kwargs.update(kwargs.pop("kwargs", {}))
        self.source__ = kwargs.copy()
        for field in fields(self, include_field=True):
            default_val = NULL_VAL
            if field.default is not dc.MISSING:
                default_val = field.default
            elif field.default_factory is not dc.MISSING:
                default_val = field.default_factory()
            setattr(self, field.name, kwargs.pop(field.name, default_val))
            if callable(method := getattr(self, f"parse_{field.name}", None)):
                setattr(self, field.name, method(getattr(self, field.name)))
        self.kwargs = kwargs
        if hasattr(self, "parse_kwargs"):
            self.kwargs = self.parse_kwargs(kwargs)
        self.validate()

    def __repr__(self):
        _fields = [f"{field_name}={repr(getattr(self, field_name))}" for field_name in fields(self) + ["kwargs"]]
        return f"<{type(self).__name__}({_fields})>"

    def validate(self):
        """Validation Method to confirm conditions are correct across multiple fields/properties"""
        return


def copy(obj: Validated) -> Validated:
    """Generates a duplicate of an object

    Returns:
        Instance of a `Validated` subclass
    """
    new_dict = {
        f_name: copy(f_val) if isinstance(f_val, Validated) else f_val
        for f_name, f_val in [
            (fld_name, getattr(obj, fld_name)) for fld_name in fields(obj)
        ]
        if not obj.source__ or f_name in obj.source__
    }
    return type(obj)(**(new_dict | obj.kwargs))


def update(obj: Validated, other: Validated) -> None:
    """Applies any values from one `Validated` instance into another.

    Similar to `dict.update()` but applies specifically to `Validated` instances to preserve
    class behaviour

    Args:
        obj: Instance of `Validated` subclass to update
        other: Instance of `Validated` subclass to copy values from

    Raises:
        TypeError: `other` is not a subclass of `Validated`
    """
    if not isinstance(other, Validated):
        raise TypeError("Only `Validated` subclasses can be supported to update from")

    for field in fields(obj):
        setattr(obj, field, getattr(other, field))
    obj.kwargs.update(other.kwargs)
    obj.source__ = other.source__


def parse_int(_min: Optional[int] = None, _max: Optional[int] = None):
    """Convenience function to parse integer values for `Validated` classes

    Args:
        _min: Minimum value of the integer range
        _max: Maximum value of the integer range

    Returns:
        Callable WrappParsed integer for the field

    Raises:
        TypeError: Input Value is not a valid Integer type
        ValueError: Input Value is not within the defined range
    """
    def _parser(_, value):
        try:
            value = int(value)
        except TypeError:
            raise TypeError("Value must be parsable to integer")
        if _min is not None and value < _min:
            raise ValueError(f"Value must be >= {_min}")
        if _max is not None and value > _max:
            raise ValueError(f"Value must be <= {_max}")
        return value

    return _parser


@dataclass
class ModuleConfig(Validated):
    """Configuration Properties to modify/alter how the `syntrend` utility behaves"""
    max_generator_retries: int = dc.field(default=int(getenv(f"{DEFAULT_ENVVAR_PREFIX}_MAX_GENERATOR_RETRIES", 20)))
    """Maximum number of retries a Generator can perform before failing.
    
    *Useful for when a distribution is applied
    """
    max_historian_buffer: int = dc.field(default=int(getenv(f"{DEFAULT_ENVVAR_PREFIX}_MAX_HISTORIAN_BUFFER", 20)))
    """Maximum values to be kept in a buffer of previous values"""
    generator_dir: str = dc.field(default=getenv(f"{DEFAULT_ENVVAR_PREFIX}_GENERATOR_DIR", ""))
    """Source Directory of Custom Generators"""

    parse_max_generator_retries = parse_int(_min=1)
    """Parse `max_generator_retries` and validates if value >= 1"""
    parse_max_historian_buffer = parse_int(_min=1)
    """Parse `max_historian_buffer` and validates if value >= 1"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def parse_generator_dir(self, value: str) -> Path:
        """Parse `generator_dir` and validates path exists and is a directory"""
        if not value:
            return ADD_GENERATOR_DIR
        parsed_path = Path(value).absolute()
        if not parsed_path.is_dir():
            raise ValueError("Source Generator Directory does not exist")
        return parsed_path


@dataclass
class OutputConfig(Validated):
    """Configuration Properties used for Global and Object-specific outputs"""
    format: str = dc.field(default="json")
    directory: Path = dc.field(default="-")
    filename_format: str = dc.field(default="{name}_{id}.{format}")
    collection: bool = dc.field(default=False)
    count: int = dc.field(default=1)
    time_field: str = dc.field(default="")

    def parse_collection(self, value):
        return bool(value)

    def parse_directory(self, value):
        if isinstance(value, Path):
            return value
        if value == "-":
            return OUTPUT_STDOUT
        p = Path(value).absolute()
        if not p.exists():
            p.mkdir(parents=True)
        assert p.is_dir(), "Path must be a directory"
        return p


# class ValueRange(BaseModel):
#     min: T_VALUE
#     max: T_VALUE
#     distribution: DistributionTypes = DistributionTypes.Linear
#     factor: float = Field(0.0)
#
#     def __init__(self, **kwargs):
#         if (
#                 "distribution" in kwargs
#                 and isinstance(kwargs["distribution"], str)
#                 and "factor" not in kwargs
#                 and DIST_SEP in kwargs["distribution"]
#         ):
#             parts = kwargs["distribution"].split(DIST_SEP)
#             kwargs["factor"] = parts[1]
#             kwargs["distribution"] = parts[0]
#         super().__init__(**kwargs)


@dataclass
class SeriesConfig(Validated):
    type: SeriesType
    count: int = dc.field(default=1)
    series_cfg: dict = dc.field(default_factory=dict)

    parse_count = parse_int(_min=1)


@dataclass
class PropertyDistribution(Validated):
    type: DistributionTypes = DistributionTypes.NoDistribution
    std_dev_factor: float = 0.
    min_offset: Union[int, float] = 0
    max_offset: Union[int, float] = 1

    def parse_type(self, value):
        if isinstance(value, DistributionTypes):
            return value
        return DistributionTypes(value)

    def validate(self):
        if self.min_offset > self.max_offset:
            raise ValueError("Distribution Min value must be lower than the Max value")


@dc.dataclass
class PropertyDefinition(Validated):
    name: str
    type: str
    distribution: Union[DistributionTypes, PropertyDistribution] = dc.field(default=DistributionTypes.NoDistribution)
    conditions: list[str] = dc.field(default_factory=list)
    expression: str = dc.field(default="")
    start: any = dc.field(default=None)
    items: list[any] = dc.field(default_factory=list)
    properties: dict[str, "PropertyDefinition"] = dc.field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def parse_distribution(self, dist_type):
        if isinstance(dist_type, str):
            dist_type = DistributionTypes(dist_type)
        if isinstance(dist_type, DistributionTypes):
            dist_type = {"type": dist_type}
        if isinstance(dist_type, dict):
            dist_type = PropertyDistribution(**dist_type)
        return dist_type

    def parse_properties(self, props):
        return {
            prop: (
                val if isinstance(val, PropertyDefinition) else
                PropertyDefinition(name=prop if "name" not in val else val["name"], **val)
            ) for prop, val in props.items()
        }


@dataclass
class ObjectDefinition(PropertyDefinition):
    output: OutputConfig = dc.field(default_factory=OutputConfig)
    series: SeriesType = dc.field(default=SeriesType.Reference)

    def parse_output(self, value):
        if isinstance(value, OutputConfig):
            return value
        return OutputConfig(**value)


@dataclass
class ProjectConfig(Validated):
    """
    Project File Configuration

    Provides
    """
    objects: dict[str, ObjectDefinition]
    output: OutputConfig = dc.field(default_factory=OutputConfig)
    config: ModuleConfig = dc.field(default_factory=ModuleConfig)

    def parse_output(self, output):
        if isinstance(output, OutputConfig):
            return output
        return OutputConfig(**output)

    def parse_config(self, config):
        if isinstance(config, ModuleConfig):
            return config
        return ModuleConfig(**config)

    def parse_objects(self, objects):
        if len(objects) == 0:
            raise ValueError("Project Config must include one object to generate")
        return {obj_name: ObjectDefinition(name=obj_name, **objects[obj_name]) for obj_name in objects}
