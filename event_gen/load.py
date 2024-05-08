from event_gen.config import model
from event_gen.utils import parse, generator

import logging
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, model_validator

LOG = logging.getLogger(__name__)


def update_module_config(config: model.ModuleConfig):
    if config.max_generator_retries:
        generator.MAX_GENERATOR_RETRIES = config.max_generator_retries
    if config.max_historian_buffer:
        generator.MAX_HISTORIAN_BUFFER = config.max_historian_buffer


def load_project(config_dict: dict):
    project_cfg = model.ProjectConfig(**config_dict)
    if project_cfg.config:
        update_module_config(project_cfg.config)

    generator_map = {}
    for object_name, object_cfg in project_cfg.objects.items():
        generator_map[object_name] = {}
        for property_name, property_config in object_cfg.properties.items():
            generator_map[object_name][property_name] = generator.PropertyGenerator(property_config)
    return project_cfg


# class ObjectDef(BaseModel):
#     schema: str | Path
#     properties: dict[str, generator.PropertyGenerator]
#
#     @model_validator(mode="after")
#     def load_schema(self):
#         if isinstance(self.schema, str):
#             self.schema = Path(self.schema)
#         return self


# class SeriesConfig(BaseModel):
#     config: Optional[model.ModuleConfig] = None
#     objects: dict[str, ObjectDef]
#
#     @model_validator(mode="after")
#     def assign_parent_to_children(self):
#         for obj_name in self.objects:
#             for k in self.objects[obj_name].properties:
#                 self.objects[obj_name].properties[k].init(self)
#         return self

