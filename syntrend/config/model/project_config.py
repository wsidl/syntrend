from syntrend.config.model.base_config import Validated, dataclass, dc
from syntrend.config.model.object_definition import ObjectDefinition
from syntrend.config.model.module_config import ModuleConfig
from syntrend.config.model.output_config import OutputConfig

from copy import deepcopy


@dataclass
class ProjectConfig(Validated):
    """Project File Configuration

    Root-Level configuration for project files.

    Attributes:
        objects (:obj:`dict[str, ObjectDefinition]`): Mapping of Object Definitions
        output (:obj:`OutputConfig`): Default properties to define how and where results are generated
        config (:obj:`ModuleConfig`): Syntrend configuration properties to modify tool behaviour
    """

    objects: dict[str, ObjectDefinition]
    output: OutputConfig = dc.field(default_factory=OutputConfig)
    config: ModuleConfig = dc.field(default_factory=ModuleConfig)

    def parse_output(self, output):
        if isinstance(output, OutputConfig):
            return output
        return OutputConfig(**output)

    def parse_config(self, config):
        if isinstance(config, ModuleConfig):
            return config
        return ModuleConfig(**config)

    def parse_objects(self, objects):
        if len(objects) == 0:
            raise ValueError(
                'Project Config must include one object to generate', {}
            ) from None
        root_output = self.source__.get('output', {})
        output_configs = {}
        for object_name in objects:
            output_configs[object_name] = deepcopy(root_output)
            output_configs[object_name].update(objects[object_name].pop('output', {}))
        return {
            object_name: ObjectDefinition(
                name=object_name,
                output=output_configs[object_name],
                **objects[object_name],
            )
            for object_name in objects
        }
