from syntrend.config import model

from typing import Union, Generator, Any
from pathlib import Path

from ruamel.yaml import YAML, error

yaml = YAML(typ="safe")
CONFIG_MODULES = [
    model.ProjectConfig,
    model.OutputConfig,
    model.ModuleConfig,
]
MODULE_KEYS = {}
for module in CONFIG_MODULES:
    yaml.register_class(module)
    MODULE_KEYS[module] = {fld.name for fld in model.dc.fields(module)}


def parse_object(config_dict: dict) -> Union[dict, model.Validated]:
    dict_keys = set(config_dict)
    for _module in MODULE_KEYS:
        if not dict_keys - MODULE_KEYS[_module]:
            return _module(**config_dict)
    return config_dict


def retrieve_source(config_file: Union[list[dict], dict, str, Path]) -> Generator[dict[str, Any], None, None]:
    if isinstance(config_file, list):
        for inner_dict in config_file:
            yield parse_object(inner_dict)
        return
    if isinstance(config_file, dict):
        yield parse_object(config_file)
        return

    content = config_file
    if (path_ref := Path(config_file)).exists():
        with path_ref.open("r") as file_obj:
            content = file_obj.read()

    try:
        for doc in yaml.load_all(content):
            yield parse_object(doc)
    except error.YAMLError as exc:
        raise ValueError(
            f"Invalid content format provided for parsing - {type(exc).__name__}: {exc.args}",
            f'Content being parsed begins with the following: "{content[:20]}..."'
        )


def load_config(config_file: Union[dict, str, Path]) -> model.ProjectConfig:
    new_config = model.ProjectConfig(objects={"test": {"type": "string"}})
    for config_obj in retrieve_source(config_file):
        if isinstance(config_obj, model.ProjectConfig):
            new_config = config_obj
        elif isinstance(config_obj, model.OutputConfig):
            new_config.output.update__(config_obj)
        elif isinstance(config_obj, model.ModuleConfig):
            new_config.config.update__(config_obj)
        elif isinstance(config_obj, dict):
            if "type" in config_obj:
                config_obj = {"this": config_obj}
            new_config.objects = model.ObjectDefinitions(**config_obj)
        else:
            raise ValueError(f"Unhandled Configuration Type: {repr(config_obj)}", config_obj)
    return new_config
