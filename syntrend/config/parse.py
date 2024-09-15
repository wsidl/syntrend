from syntrend.config import model

from typing import Union, Generator, Any
from pathlib import Path

from ruamel.yaml import YAML, error

yaml = YAML(typ='safe')
CONFIG_MODULES = [
    model.ProjectConfig,
    model.OutputConfig,
    model.ModuleConfig,
]
MODULE_KEYS = {}
for module in CONFIG_MODULES:
    yaml.register_class(module)
    MODULE_KEYS[module] = set(model.fields(module))


def parse_object(config_dict: dict) -> Union[dict, model.Validated]:
    dict_keys = set(config_dict)
    for _module in MODULE_KEYS:
        if not dict_keys - MODULE_KEYS[_module]:
            return _module(**config_dict)
    return config_dict


def retrieve_source(
    config_file: Union[list[dict], dict, str, Path],
) -> Generator[dict[str, Any], None, None]:
    if isinstance(config_file, list):
        for inner_dict in config_file:
            yield parse_object(inner_dict)
        return
    if isinstance(config_file, dict):
        yield parse_object(config_file)
        return

    content = config_file
    if (path_ref := Path(config_file)).exists():
        with path_ref.open('r') as file_obj:
            content = file_obj.read()

    try:
        for doc in yaml.load_all(content):
            yield doc
    except error.YAMLError as err:
        raise ValueError(
            f'Invalid content format provided for parsing - {type(err).__name__}: {err.args}',
            {"File Header": content[:20]}
        ) from None


def load_config(config_file: Union[dict, str, Path]) -> model.ProjectConfig:
    new_config = model.ProjectConfig(objects={'test': {'type': 'string'}})
    for config_obj in retrieve_source(config_file):
        if isinstance(config_obj, model.ProjectConfig):
            new_config = config_obj
        elif isinstance(config_obj, model.OutputConfig):
            model.update(new_config.output, config_obj)
        elif isinstance(config_obj, model.ModuleConfig):
            model.update(new_config.config, config_obj)
        elif isinstance(config_obj, dict):
            if 'type' in config_obj:
                config_obj = {'this': config_obj}
            new_config.objects = {
                obj_name: model.ObjectDefinition(name=obj_name, **config_obj[obj_name])
                for obj_name in config_obj
            }
        else:
            raise ValueError(
                f'Unhandled Configuration Type: {repr(config_obj)}',
                {'Config Object Type': type(config_obj).__name__}
            )
    return new_config
