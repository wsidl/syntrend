from pathlib import PurePath, Path
from typing import Union, Optional
import json
import yaml
from yaml.parser import ParserError


def parse_content_format(_input: Union[str, PurePath, dict]) -> dict:
    if isinstance(_input, dict):
        return _input

    content = _input
    if (path_ref := Path(content)).exists():
        with path_ref.open("r") as file_obj:
            content = file_obj.read()
    try:
        # First with JSON since it's more restrictive
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    try:
        return yaml.safe_load(content)
    except ParserError:
        raise ValueError(
            "Invalid content format provided for parsing",
            f'First segments attempted to format contains: "{content[:20]}..."'
        )
