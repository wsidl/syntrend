from event_gen.config import model

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
    for _cfg in [
        config_dict,
        {"objects": config_dict},
        {"objects": {"self": config_dict}}
    ]:
        try:
            return model.ProjectConfig(**_cfg)
        except TypeError as exc:
            if not _error:
                _error = exc
    raise ValueError(f"Invalid Project Configuration: {_error}")
