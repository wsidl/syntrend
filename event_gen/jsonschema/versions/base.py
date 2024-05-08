import typing
from urllib.parse import urlparse, ParseResult
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Any


class Version:
    pass


class Element(BaseModel):
    _aliases: dict[str, str]
    _parent: "Element"
    _field_type_map: dict[str, "Element"]

    @classmethod
    def load_object(cls, schema, context) -> "Element":
        path = "/".join([context["path"], context["name"]])
        if path.startswith("/"):
            path = path[1:]
        for k in schema:
            if k in cls._aliases:
                schema[cls._aliases[k]] = schema[k]
                del schema[k]
        new_object = cls(**schema)
        new_context = context | {"parent": new_object, "path": path}
        for fld in cls.model_fields():
            if isinstance(schema[fld.name], fld.type):
                continue
            if fld.name not in cls._field_type_map:
                continue
            new_context |= {}
            print(fld.type)
            schema[fld.name] = cls._field_type_map[fld.name].load_object(schema[fld.name], new_context)
            #TODO: Incomplete line -> getattr(new_object, fld.name).l
        return new_object

    def pre_parse(self):
        pass

    def post_parse(self):
        pass

    def parse(self):
        self.pre_parse()
        for child in self.__children:
            self.__getattribute__(child).parse()
        self.post_parse()

    def get_context(self, arg: str):
        return self.__context[arg]

    def get_definition(self, ref: str) -> "Element":
        return self.get_context("parent").get_definition(ref)

    def generate(self) -> Any:
        raise NotImplementedError("This object cannot generate a new value")


class RootElement(Element):
    pass
