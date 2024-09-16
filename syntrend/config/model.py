"""Project File Schema"""

import logging
from typing import Union, Optional
import dataclasses as dc
from enum import Enum
from os import getenv
from pathlib import Path
from functools import partial

LOG = logging.getLogger(__name__)
DEFAULT_ENV_VAR_PREFIX = 'SYNTREND_'
OUTPUT_STDOUT = Path('-')
DEFAULT_FILE_FORMAT = '{name}-{id}.{format}'
USER_CONFIG_DIR = Path.home().joinpath('.config', 'syntrend')
ADD_GENERATOR_DIR = USER_CONFIG_DIR.joinpath('generators')

dataclass = partial(dc.dataclass, kw_only=True, init=False)


class NullValue:
    pass


class _NullInt(NullValue, int):
    pass


class _NullString(NullValue, str):
    pass


NULL_VAL = NullValue()
NULL_INT = _NullInt(0)
NULL_STR = _NullString('')


class DistributionTypes(Enum):
    NoDistribution = 'none'
    Linear = 'linear'
    StandardDeviation = 'std_dev'


class Progress(Enum):
    Trend = 'trend'
    Last = 'last'


def fields(obj: dc.dataclass, include_field=False) -> list[str | dc.Field]:
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
        kwargs.update(kwargs.pop('kwargs', {}))
        self.source__ = kwargs.copy()
        for field in fields(self, include_field=True):
            default_val = NULL_VAL
            if field.default is not dc.MISSING:
                default_val = field.default
            elif field.default_factory is not dc.MISSING:
                default_val = field.default_factory()
            setattr(self, field.name, kwargs.pop(field.name, default_val))
            if callable(method := getattr(self, f'parse_{field.name}', None)):
                setattr(self, field.name, method(getattr(self, field.name)))
        self.kwargs = kwargs
        if hasattr(self, 'parse_kwargs'):
            self.kwargs = self.parse_kwargs(kwargs)
        self.validate()

    def __repr__(self):
        _fields = [
            f'{field_name}={repr(getattr(self, field_name))}'
            for field_name in fields(self) + ['kwargs']
        ]
        return f'<{type(self).__name__}({_fields})>'

    def validate(self):
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
        raise TypeError(
            'Only `Validated` subclasses can be supported to update from',
            {
                'Original Object Type': type(obj).__name__,
                'Other Object Type': type(other).__name__,
            }
        )

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
            raise TypeError(
                'Value must be parsable to integer',
                {
                    'Input Value': str(value),
                    'Input Value Type': type(value).__name__,
                }
            ) from None
        if _min is not None and value < _min:
            raise ValueError(
                'Provided value is less than the minimum allowed',
                {
                    'Input Value': str(value),
                    'Minimum': _min,
                }
            )
        if _max is not None and value > _max:
            raise ValueError(
                'Provided value is greater than the maximum allowed',
                {
                    'Input Value': str(value),
                    'Maximum': _max,
                }
            )
        return value

    return _parser


@dataclass
class ModuleConfig(Validated):
    """Configuration Properties to modify/alter how the `syntrend` utility behaves"""

    max_generator_retries: int = dc.field(
        default=int(getenv(f'{DEFAULT_ENV_VAR_PREFIX}_MAX_GENERATOR_RETRIES', 20))
    )
    """Maximum number of retries a Generator can perform before failing."""
    max_historian_buffer: int = dc.field(
        default=int(getenv(f'{DEFAULT_ENV_VAR_PREFIX}_MAX_HISTORIAN_BUFFER', 20))
    )
    """Maximum values to be kept in a buffer of previous values"""
    generator_dir: str = dc.field(
        default=getenv(f'{DEFAULT_ENV_VAR_PREFIX}_GENERATOR_DIR', '')
    )
    """Source Directory of Custom Generators"""

    parse_max_generator_retries = parse_int(_min=1)
    parse_max_historian_buffer = parse_int(_min=1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def parse_generator_dir(self, value: str) -> Path:
        if not value:
            return ADD_GENERATOR_DIR
        parsed_path = Path(value).absolute()
        if not parsed_path.is_dir():
            raise ValueError(
                'Source Generator Directory does not exist',
                {
                    'Input Path': value,
                    'Parsed Path': str(parsed_path),
                }
            )
        return parsed_path


@dataclass
class OutputConfig(Validated):
    """Configuration Properties used for Global and Object-specific outputs"""

    format: str = dc.field(default='json')
    directory: Path = dc.field(default='-')
    filename_format: str = dc.field(default='{name}_{id}.{format}')
    collection: bool = dc.field(default=False)
    count: int = dc.field(default=1)
    time_field: str = dc.field(default='')

    def parse_collection(self, value):
        return bool(value)

    def parse_directory(self, value):
        if isinstance(value, Path):
            return value
        if value == '-':
            return OUTPUT_STDOUT
        p = Path(value).absolute()
        if not p.exists():
            p.mkdir(parents=True)
        assert p.is_dir(), 'Path must be a directory'
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
class PropertyDistribution(Validated):
    """Distribution Definition

    Configurations to support how values will vary from its original value

    Attributes:
        type (:obj:`DistributionTypes`): The type of distribution to apply. Defaults to "none"
        std_dev (:obj:`float`, optional): The standard deviation of the distribution
        min_offset (:obj:`float`, optional): The minimum offset of the distribution
        max_offset (:obj:`float`, optional): The maximum offset of the distribution
    """
    type: DistributionTypes = DistributionTypes.NoDistribution
    std_dev: float = 0.0
    min_offset: Union[int, float] = 0
    max_offset: Union[int, float] = 1

    def parse_type(self, value):
        if isinstance(value, DistributionTypes):
            return value
        return DistributionTypes(value)

    def validate(self):
        if self.min_offset > self.max_offset:
            raise ValueError(
                'Distribution Min value must be lower than the Max value',
                {
                    'Minimum Value': self.min_offset,
                    'Maximum Value': self.max_offset,
                }
            )


@dc.dataclass
class PropertyDefinition(Validated):
    """Property Definition

    Definition of how a value is generated and any associated properties to modify its behaviour

    Attributes:
        type (:obj:`str`): Generator Type to be used for this Property Definition
        distribution (:obj:`PropertyDistribution`): Property to define how the generated values will vary using a
            :obj:`DistributionTypes`. Defaults to "none"
        expression (:obj:`str`): String Expression to define a trend, behaviour, or conditions to apply.

            See Also:
                For more information on Expressions, see `Expressions <docs/expressions>`__.
        start: Any value associated with :obj:`type` for when a previous value is expected but none available.
        items (:obj:`list`): List of items required for Generator Types needing a list of objects to choose from.
        properties (:obj:`dict[str, PropertyDefinition]`): Mapping of sub properties namely to support nested objects.
    """
    name: str
    type: str
    distribution: Union[DistributionTypes, PropertyDistribution] = dc.field(
        default=DistributionTypes.NoDistribution
    )
    conditions: list[str] = dc.field(default_factory=list)
    expression: str = dc.field(default='')
    start: any = dc.field(default=None)
    items: list[any] = dc.field(default_factory=list)
    properties: dict[str, 'PropertyDefinition'] = dc.field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def parse_distribution(self, dist_type):
        if isinstance(dist_type, str):
            dist_type = DistributionTypes(dist_type)
        if isinstance(dist_type, DistributionTypes):
            dist_type = {'type': dist_type}
        if isinstance(dist_type, dict):
            dist_type = PropertyDistribution(**dist_type)
        return dist_type

    def parse_properties(self, props):
        return {
            prop: (
                val
                if isinstance(val, PropertyDefinition)
                else PropertyDefinition(
                    name=prop if 'name' not in val else val['name'], **val
                )
            )
            for prop, val in props.items()
        }


@dataclass
class ObjectDefinition(PropertyDefinition):
    """Object Definition

    Extended definition of :obj:`PropertyDefinition` to support root-level object behaviour

    Attributes:
        output (:obj:`OutputConfig`): Properties to define how and where results are generated
    """
    output: OutputConfig = dc.field(default_factory=OutputConfig)

    def parse_output(self, value):
        if isinstance(value, OutputConfig):
            return value
        return OutputConfig(**value)


@dataclass
class ProjectConfig(Validated):
    """Project File Configuration

    Root-Level configuration for project files.

    Attributes:
        objects (:obj:`dict[str, ObjectDefinition]`): Mapping of Object Definitions
        output (:obj:`OutputConfig`): Default properties to define how and where results are generated
        config (:obj:`ModuleConfig`): Syntrend configuration properties to modify tool behaviour
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
            raise ValueError('Project Config must include one object to generate', {})
        return {
            obj_name: ObjectDefinition(name=obj_name, **objects[obj_name])
            for obj_name in objects
        }
