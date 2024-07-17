from syntrend.config import model

from typing import Union
from pathlib import Path

from yaml import safe_load, parser


def retrieve_source(config_file: Union[dict, str, Path]):
    if isinstance(config_file, dict):
        return config_file

    content = config_file
    if (path_ref := Path(config_file)).exists():
        with path_ref.open("r") as file_obj:
            content = file_obj.read()

    try:
        return safe_load(content)
    except parser.ParserError as exc:
        raise ValueError(
            "Invalid content format provided for parsing",
            f'Content being parsed begins with the following: "{content[:20]}..."'
        )


def load_config(config_file: Union[dict, str, Path]) -> model.ProjectConfig:
    config_dict = retrieve_source(config_file)

    _error = None
    if "objects" in config_dict and "type" not in config_dict:
        return model.ProjectConfig(**config_dict)
    if "type" in config_dict and "config" not in config_dict and "objects" not in config_dict:
        return model.ProjectConfig(**{"objects": {"this": config_dict}})
    return model.ProjectConfig(**{"objects": config_dict})
