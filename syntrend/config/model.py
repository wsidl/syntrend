import logging
from typing import Union, Type
import dataclasses as dc
from enum import Enum
from os import getenv
from pathlib import Path

LOG = logging.getLogger(__name__)
OUTPUT_STDOUT = Path("-")
DEFAULT_FILE_FORMAT = "{name}-{id}.{format}"
USER_CONFIG_DIR = Path.home().joinpath(".config", "syntrend")
ADD_GENERATOR_DIR = USER_CONFIG_DIR.joinpath("generators")


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


@dc.dataclass
class Validated:
    def __post_init__(self):
        """Run validation methods if declared.
        The validation method can be a simple check
        that raises ValueError or a transformation to
        the field value.
        The validation is performed by calling a function named:
            `parse_<field_name>(self, value, field) -> field.type`
        """
        for field in dc.fields(self):
            if callable(method := getattr(self, f"parse_{field.name}", None)):
                setattr(self, field.name, method(getattr(self, field.name)))
        self.validate()

    def validate(self):
        return

    def to_dict__(self) -> dict:
        return dc.asdict(self)

    def copy__(self):
        return self.__class__(**{
            f_name: f_val.copy__() if isinstance(f_val, Validated) else f_val
            for f_name, f_val in [
                (fld.name, getattr(self, fld.name)) for fld in dc.fields(self)
            ]
        })

    def update__(self, other) -> None:
        assert isinstance(other, self.__class__), "Can only update from a matching dataclass type"
        for field in dc.fields(self):
            other_field = getattr(other, field.name)
            if isinstance(other_field, Validated):
                getattr(self, field.name).update__(other_field)
                continue
            if isinstance(other_field, dict):
                current_keys = set(getattr(self, field.name))
                for prop in other_field:
                    if isinstance(other_field[prop], Validated):
                        if prop not in current_keys:
                            getattr(self, field.name)[prop] = other_field[prop].copy__()
                        else:
                            getattr(self, field.name)[prop].update__(other_field[prop])
                        continue
                    getattr(self, field.name)[prop] = other_field[prop]
                continue
            setattr(self, field.name, getattr(other, field.name))

    def into__(self, other_cls: Type["Validated"]) -> "Validated":
        current_fieldset = set(fld.name for fld in dc.fields(self))
        new_fieldset = set(fld.name for fld in dc.fields(other_cls))
        assert len(new_fieldset - current_fieldset) == 0, "Target Object contains fields not in current object"
        return other_cls(**{
            fld.name: getattr(self, fld.name) for fld in dc.fields(other_cls)
        })


def parse_int(_min=None, _max=None):
    def _parser(_, value):
        try:
            value = int(value)
        except TypeError:
            raise TypeError("Value must parsable to integer")
        if _min is not None:
            assert value >= _min, f"Value must be >= {_min}"
        if _max is not None:
            assert value <= _max, f"Value must be <= {_max}"
        return int(value)

    return _parser


@dc.dataclass
class ModuleConfig(Validated):
    max_generator_retries: int = dc.field(default=20)
    max_historian_buffer: int = dc.field(default=20)
    generator_dir: str = dc.field(default=getenv("SYNTREND_GENERATOR_DIR", str(ADD_GENERATOR_DIR)))

    parse_max_generator_retries = parse_int(_min=1)
    parse_max_historian_buffer = parse_int(_min=1)


@dc.dataclass
class OutputConfig(Validated):
    """

    """
    format: str = dc.field(default="json")
    directory: Path = dc.field(default="-")
    filename_format: str = dc.field(default="{name}_{id}.{format}")
    aggregate: bool = dc.field(default=False)
    count: int = dc.field(default=1)

    def parse_output_dir(self, value):
        if isinstance(value, Path):
            return value
        if value == "-":
            return OUTPUT_STDOUT
        p = Path(value).absolute()
        if not p.exists():
            p.mkdir(parents=True)
        assert p.is_dir(), "Path must be a directory"
        return p

    def validate(self):
        if isinstance(self.aggregate, (str, int)):
            self.aggregate = bool(self.aggregate)


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


@dc.dataclass(init=False)
class SeriesConfig(Validated):
    type: SeriesType
    count: int = dc.field(default=1)
    series_cfg: dict = dc.field(default_factory=dict)

    def __init__(self, **kwargs):
        self.type = SeriesType(kwargs.pop("type", "reference").lower())
        self.count = int(kwargs.pop("count", 1))
        self.series_cfg = kwargs


@dc.dataclass
class PropertyDistribution(Validated):
    type: DistributionTypes = DistributionTypes.NoDistribution
    std_dev_factor: float = 0.
    min_offset: Union[int, float] = 0
    max_offset: Union[int, float] = 0

    def validate(self):
        assert self.min_offset <= self.max_offset, f"Min value '{self.min_offset}' must be lower than the Max value '{self.max_offset}'"


@dc.dataclass(init=False)
class PropertyDefinition(Validated):
    name: str
    type: str
    distribution: Union[DistributionTypes, PropertyDistribution] = dc.field(default=DistributionTypes.NoDistribution)
    conditions: list[str] = dc.field(default_factory=list)
    expression: str = ""
    start: any = None
    items: list[any] = dc.field(default_factory=list)
    properties: dict[str, "PropertyDefinition"] = dc.field(default_factory=dict)
    kwargs: dict = dc.field(default_factory=dict)

    def __init__(self, **kwargs):
        self.name = kwargs.pop("name")
        self.type = kwargs.pop("type").lower()
        self.conditions = []
        self.properties = {}
        self.expression = kwargs.pop("expression", "")
        self.distribution = PropertyDistribution()
        self.start = kwargs.pop("start", None)
        self.items = kwargs.pop("items", [])
        if dist_type := kwargs.pop("distribution", {}):
            if isinstance(dist_type, str):
                dist_type = DistributionTypes(dist_type)
            if isinstance(dist_type, DistributionTypes):
                dist_type = {"type": dist_type}
            if isinstance(dist_type, dict):
                dist_type = PropertyDistribution(**dist_type)
            self.distribution = dist_type
        if "conditions" in kwargs:
            self.conditions = kwargs.pop("conditions")
        if "properties" in kwargs:
            self.properties = {
                prop: val.copy__() if isinstance(val, PropertyDefinition) else PropertyDefinition(name=prop if "name" not in val else val["name"], **val)
                for prop, val in kwargs.pop("properties").items()
            }
        if "kwargs" in kwargs:
            kwargs.update(kwargs.pop("kwargs"))
        self.kwargs = kwargs


@dc.dataclass(init=False)
class ObjectDefinition(PropertyDefinition):
    output: OutputConfig = dc.field(default_factory=OutputConfig)
    series: SeriesType = dc.field(default=SeriesType.Reference)

    def __init__(self, **kwargs):
        self.output = OutputConfig(**kwargs.pop("output", {}))
        self.series = SeriesType(kwargs.pop("series", "reference"))
        super().__init__(**kwargs)

    def parse_output(self, value):
        if isinstance(value, OutputConfig):
            return value
        return OutputConfig(**value)


class ObjectDefinitions(dict):
    def __new__(cls, **kwargs):
        for object_name in kwargs:
            if isinstance(kwargs[object_name], dict):
                kwargs[object_name] = ObjectDefinition(name=object_name, **kwargs[object_name])
        return kwargs


@dc.dataclass
class ProjectConfig(Validated):
    """
    Project File Configuration

    Provides
    """
    objects: Union[ObjectDefinitions, dict[str, Union[dict, ObjectDefinition]]]
    output: OutputConfig = dc.field(default_factory=OutputConfig)
    config: ModuleConfig = dc.field(default_factory=ModuleConfig)

    def parse_objects(self, objects):
        if len(objects) == 0:
            raise ValueError("Project Config must include one object to generate")
        return ObjectDefinitions(**objects)
