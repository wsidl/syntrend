from syntrend.config import model
from syntrend.config.parse import parser

from typing import Type

CONFIG_MODULES = [
    model.ProjectConfig,
    model.ModuleConfig,
    model.ObjectDefinition,
    model.PropertyDefinition,
]
MODULE_KEYS: dict[Type[model.Validated], set[str]] = {}

for module in CONFIG_MODULES:
    parser.yaml.register_class(module)
    MODULE_KEYS[module] = set(model.fields(module))


def parse_object(config_dict: dict, test=False) -> model.Validated | None:
    if isinstance(config_dict, model.DocumentLink):
        config_dict = config_dict.get_reference()
    dict_keys = set(config_dict)
    for _module in MODULE_KEYS:
        if not dict_keys - MODULE_KEYS[_module]:
            return _module(**config_dict)

    if test:
        return None

    # Failed to parse valid object, attempt project shortcut
    has_nested_objects = isinstance(config_dict[list(config_dict.keys())[0]], dict)
    if has_nested_objects and (
        new_object := parse_object({'objects': config_dict}, True)
    ):
        return new_object
    return parse_object({'objects': {'this': config_dict}}, True)
