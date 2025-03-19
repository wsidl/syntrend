from syntrend.config.model.base_config import Validated, dataclass
from syntrend.config.model.enum import DistributionTypes


@dataclass
class PropertyDistribution(Validated):
    """Distribution Definition

    Configurations to support how values will vary from its original value

    Attributes:
        type (:obj:`DistributionTypes`): The type of distribution to apply. Defaults to "none"
        std_dev (:obj:`float`, optional): The standard deviation of the distribution
        min_offset (:obj:`float`, optional): The minimum offset of the distribution
        max_offset (:obj:`float`, optional): The maximum offset of the distribution
    """

    type: DistributionTypes = DistributionTypes.NoDistribution
    std_dev: float = 0.0
    min_offset: int | float = 0
    max_offset: int | float = 1

    def parse_type(self, value):
        if isinstance(value, DistributionTypes):
            return value
        return DistributionTypes(value)

    def validate_(self):
        if self.min_offset > self.max_offset:
            raise ValueError(
                'Distribution Min value must be lower than the Max value',
                {
                    'Minimum Value': self.min_offset,
                    'Maximum Value': self.max_offset,
                },
            )
