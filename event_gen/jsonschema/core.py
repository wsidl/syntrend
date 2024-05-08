from event_gen.utils.parse import parse_content_format
from event_gen.jsonschema.versions import base, v2020_12

from typing import Union, Optional, TYPE_CHECKING, Type
from enum import Enum
from pathlib import PurePath
import re

if TYPE_CHECKING:
    from pathlib import PurePath


R_SCHEMA_URI = re.compile(r"https://json-schema.org/([\w\-/]+)/schema")
T_VERSION_REF = Union[str]


class SchemaVersion(Enum):
    Draft4 = "draft-04"
    Draft6 = "draft-06"
    Draft7 = "draft-07"
    V2019_09 = "draft/2019-09"
    V2020_12 = "draft/2020-12"
    Default = "draft/2020-12"


VERSIONS = {
    SchemaVersion.Draft4: base.Version,
    SchemaVersion.Draft6: base.Version,
    SchemaVersion.V2019_09: base.Version,
    SchemaVersion.V2020_12: v2020_12.Version202012
}


def get_version(version_ref: Union[str, SchemaVersion]) -> SchemaVersion:
    version_val = version_ref
    if isinstance(version_val, str):
        if match := R_SCHEMA_URI.match(version_val):
            version_val = match.group(1)
        try:
            version_val = SchemaVersion(version_val)
        except ValueError:
            raise ValueError("Provided Version Reference is not a valid JSON Schema version: %s", version_ref)
    return version_val


class SchemaManager:
    def __init__(self):
        self.__schemas: dict[str, base.Element] = {}

    def add_schema(
            self,
            reference_name: str,
            schema_content: Union[str, PurePath, dict],
            schema_version: Optional[Union[str, SchemaVersion]] = None,
    ):
        _ctx = {
            "path": "",
            "name": "#"
        }
        content = parse_content_format(schema_content)
        if isinstance(schema_version, str):
            schema_version = SchemaVersion(schema_version)
        if not schema_version:
            if "$schema" in content:
                schema_version = get_version(content["$schema"])
            else:
                schema_version = SchemaVersion.Default
        self.__schemas[reference_name] = VERSIONS[schema_version](**content)

    def get_schema(self, reference_name: str) -> base.Element:
        return self.__schemas[reference_name]
