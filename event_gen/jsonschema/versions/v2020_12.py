from event_gen.jsonschema.versions import base
from typing import Any
from enum import Enum


class Reference(base.Element):
    _aliases = {"$ref": "ref"}
    ref: str


class RootDefinitionType(Enum):
    Boolean = "boolean"
    Object = "object"


class DefinitionType(Enum):
    Boolean = "boolean"
    Object = "object"
    Integer = "integer"
    String = "string"


class Property(base.Element):
    ref: str = base.Field(alias="$ref", default="")
    description: str = ""
    type: DefinitionType = DefinitionType.String

    @base.field_validator("ref", "type", mode="before")
    def validate_ref(cls, value, values):
        if not value:
            assert "type" in values, "`type` must be defined"
        return value

    def generate(self):
        # TODO: Prepare Generator Entity
        pass


COMPLEX_TYPE_MAP = {
    "object": dict,
}

PRIMITIVE_TYPE_MAP = {
    "string": str,
    "integer": int,
    "boolean": bool
}

SET_KEY_DEFS = {"$defs", "definitions"}
FIELD_ALIASES = {"definition": "$defs", "_id": "$id", "schema": "$schema"}


def deref_definitions(name: str, schema: dict[str, dict], context, def_map_callback):
    def_key = list(set(schema.keys()) & SET_KEY_DEFS)
    if not def_key:
        return schema

    _id = schema.pop("$id", "")
    base_path = (context["base_path"] if not _id else "#") + "/" + name
    defs = schema.pop(def_key[0], {})
    def_map = {"/".join([base_path, def_key[0], def_name]): defs[def_name] for def_name in defs}

    def get_reference_lookup(key: str) -> Any:
        for def_key in def_map:
            if key.startswith(def_key):
                key_parts = key[len(def_key) + 1:].split("/")
                return_schema = def_map[def_key]
                for key_part in key_parts:
                    return_schema = return_schema[key_part]
                return return_schema
        if _id:
            raise KeyError(f'Reference "{key}" could not be found')
        return context["get_reference_lookup"](key)

    for def_name, def_schema in defs.items():
        def_map[def_name] = def_map_callback(def_name, def_schema, context | {"base_path": base_path, "get_reference_lookup": get_reference_lookup})


def generate_model(schema: dict[str, str]):
    definitions = schema.pop("$defs", schema.pop("definitions", {}))

    required = schema.pop("required")
    schema_id = schema.pop("$id", "")
    _type = schema.pop("type")
    validators = {}
    context_map = {
        "defs": {name: definitions[name] for name in definitions}
    }

    if _type in COMPLEX_TYPE_MAP:
        new_object = COMPLEX_TYPE_MAP[_type]()
        properties = schema.pop("properties")


class RootElement(base.RootElement):
    schema_id: str = base.Field(default="", alias="$id")
    schema_ref: str = base.Field(default="", alias="$alias")
    type: RootDefinitionType = base.Field(default=RootDefinitionType.Object)
    definitions: dict[str, "RootElement"] = base.Field(alias="$defs", default_factory=dict)
    properties: dict[str, Property]
    required: list[str] = base.Field(default_factory=list)

    def get_definition(self, ref: str) -> "RootElement":
        if ref in self.definitions:
            return self.definitions[ref]
        if self._id:
            raise ValueError(f'Definition "{ref}" does not exist in this definition scope')
        super().get_definition(ref)


class Version202012(RootElement):
    pass
