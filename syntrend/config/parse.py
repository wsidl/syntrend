from syntrend.config import model

from typing import Union, Generator, Any
from pathlib import Path
import re

from ruamel.yaml import YAML, error

RE_INCLUDE_REF = re.compile(r"^(.*?) ?(\d*)")
CONFIG_MODULES = [
    model.ProjectConfig,
    model.OutputConfig,
    model.ModuleConfig,
]
MODULE_KEYS = {}
T_CONFIG_INPUT = list[dict] | dict | str | Path

yaml = YAML(typ='safe')
for module in CONFIG_MODULES:
    yaml.register_class(module)
    MODULE_KEYS[module] = set(model.fields(module))


def parse_object(config_dict: dict) -> Union[dict, model.Validated]:
    dict_keys = set(config_dict)
    for _module in MODULE_KEYS:
        if not dict_keys - MODULE_KEYS[_module]:
            return _module(**config_dict)
    return config_dict


def retrieve_source(config_file: T_CONFIG_INPUT) -> Generator[dict[str, Any], None, None]:
    if isinstance(config_file, list):
        for inner_dict in config_file:
            yield inner_dict
        return
    if isinstance(config_file, dict):
        yield config_file
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
    for config_dict in retrieve_source(config_file):
        config_obj = parse_object(config_dict)
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


def yaml_include(loader, node):
    if not (match := RE_INCLUDE_REF.fullmatch(node.value)):
        raise ValueError(
            'Invalid "!include" reference',
            {
                "Value": node.value
            }
        )
    path_ref, index = match.groups()
    y = loader.loader
    _yaml = YAML(typ=y.typ, pure=y.pure)  # same values as including YAML
    _yaml.composer.anchors = loader.composer.anchors
    if not index:
        index = 0
    index = int(index)
    count = 0
    for doc in retrieve_source(Path(path_ref)):
        if count == index:
            return doc
        count += 1


yaml.Constructor.add_constructor('!include', yaml_include)
