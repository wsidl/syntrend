from syntrend.config.model.document_tags import DocumentLink, DOCUMENTS
import dataclasses as dc
from functools import partial
from copy import deepcopy
from os import linesep

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


def fields(obj: dc.dataclass, include_field=False) -> list[str | dc.Field]:
    return [field if include_field else field.name for field in dc.fields(obj)]


def deep_update(base_object, new_object):
    for k, v in new_object.items():
        if k not in base_object:
            base_object[k] = v
            continue
        if isinstance(v, dict) and isinstance(base_object[k], dict):
            base_object[k] = deep_update(base_object.get(k, {}), v)
            continue
        base_object[k] = v
    return base_object


def parse_bases(base_object: dict) -> dict:
    if not (base_references := base_object.pop('_bases', [])):
        if not (base_references := base_object.pop('bases', [])):
            return base_object

    if isinstance(base_references, dict):
        base_references = [base_references]

    ref_object = {}
    for base in base_references:
        path_ref = DOCUMENTS.current_file
        if 'path' in base:
            file_path = base.pop('path', DOCUMENTS.current_file)
            path_ref = DOCUMENTS.current_file.parent.joinpath(file_path)
            if not path_ref.exists():
                raise ValueError(
                    'Path to Object Reference does not exist',
                    {
                        'Current File': DOCUMENTS.current_file,
                        'Object Summary': str(base_object),
                        'Given Path': file_path,
                        'Parsed Path': str(path_ref),
                    },
                )
        base_ref = {
            'ref': base.pop('ref', ...),
            'path': path_ref,
            'index': int(base.pop('index', 0)),
        }
        new_doc = DOCUMENTS.get_reference(base_ref)
        ref_object = deep_update(ref_object, new_doc)
    new_object = deep_update(ref_object, base_object)
    return new_object


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
        kwargs = parse_bases(kwargs)

        self.source__ = deepcopy(kwargs)
        for field in fields(self, include_field=True):
            if field.name.endswith('_'):
                continue
            default_val = NULL_VAL
            if field.default is not dc.MISSING:
                default_val = field.default
            elif field.default_factory is not dc.MISSING:
                default_val = field.default_factory()

            field_value = kwargs.get(field.name, None)
            if isinstance(field_value, DocumentLink):
                kwargs[field.name] = field_value.get_reference()
            elif isinstance(field_value, dict):
                for field_key in field_value:
                    if isinstance(field_value[field_key], DocumentLink):
                        kwargs[field.name][field_key] = field_value[
                            field_key
                        ].get_reference()
            elif isinstance(field_value, list):
                for list_index in range(len(field_value)):
                    if isinstance(kwargs[field.name][list_index], DocumentLink):
                        kwargs[field.name][list_index] = kwargs[field.name][
                            list_index
                        ].get_reference()

            setattr(self, field.name, kwargs.pop(field.name, default_val))
            if callable(method := getattr(self, f'parse_{field.name}', None)):
                setattr(self, field.name, method(getattr(self, field.name)))
        self.kwargs = kwargs
        if hasattr(self, 'parse_kwargs'):
            self.kwargs = self.parse_kwargs(kwargs)
        self.validate_()

    def __str__(self):
        _fields = []
        for field_name in fields(self) + ['kwargs']:
            new_lines = []
            obj = getattr(self, field_name)
            if isinstance(obj, dict):
                sub_lines = []
                if len(obj) == 0:
                    sub_lines = ['{}']
                else:
                    sub_lines.append('{')
                    for key in obj:
                        sub_lines += [f'    {key}:'] + [
                            '      ' + line for line in str(obj[key]).split(linesep)
                        ]
                    sub_lines.append('  }')
                new_lines += sub_lines
            else:
                new_lines = ['  ' + line for line in str(obj).split(linesep)]
                new_lines[0] = new_lines[0].strip()
            _fields.append(f'  {field_name}={linesep.join(new_lines)}')

        return f'<{type(self).__name__}({linesep}{linesep.join(_fields)}{linesep})>'

    def validate_(self):
        return

    def copy_(self) -> 'Validated':
        """Generates a duplicate of an object

        Returns:
            Instance of a `Validated` subclass
        """
        new_dict = {
            f_name: f_val.copy_() if isinstance(f_val, Validated) else f_val
            for f_name, f_val in [
                (fld_name, getattr(self, fld_name)) for fld_name in fields(self)
            ]
            if not self.source__ or f_name in self.source__
        }
        return type(self)(**(new_dict | self.kwargs))

    def update_(self, other: 'Validated') -> None:
        """Applies any values from one `Validated` instance into another.

        Similar to `dict.update()` but applies specifically to `Validated` instances to preserve
        class behaviour

        Args:
            other: Instance of `Validated` subclass to copy values from

        Raises:
            TypeError: `other` is not a subclass of `Validated`
        """
        if not isinstance(other, Validated):
            raise TypeError(
                'Only `Validated` subclasses can be supported to update from',
                {
                    'Original Object Type': type(self).__name__,
                    'Other Object Type': type(other).__name__,
                },
            )

        for field in fields(self):
            setattr(self, field, getattr(other, field))
        self.kwargs.update(other.kwargs)
        self.source__ = other.source__


def parse_int(_min: int | None = None, _max: int | None = None):
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
                },
            ) from None
        if _min is not None and value < _min:
            raise ValueError(
                'Provided value is less than the minimum allowed',
                {
                    'Input Value': str(value),
                    'Minimum': _min,
                },
            )
        if _max is not None and value > _max:
            raise ValueError(
                'Provided value is greater than the maximum allowed',
                {
                    'Input Value': str(value),
                    'Maximum': _max,
                },
            )
        return value

    return _parser
