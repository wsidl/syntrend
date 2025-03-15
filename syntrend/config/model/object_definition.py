from syntrend.config.model.base_config import dataclass, dc
from syntrend.config.model.property_definition import PropertyDefinition
from syntrend.config.model.output_config import OutputConfig


@dataclass
class ObjectDefinition(PropertyDefinition):
    """Object Definition

    Extended definition of :obj:`PropertyDefinition` to support root-level object behaviour

    Attributes:
        output (:obj:`OutputConfig`): Properties to define how and where results are generated
    """

    output: OutputConfig = dc.field(default_factory=OutputConfig)

    def parse_output(self, value):
        if isinstance(value, OutputConfig):
            return value
        return OutputConfig(**value)
