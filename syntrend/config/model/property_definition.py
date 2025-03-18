from syntrend.config.model.base_config import Validated, dataclass, dc, parse_bases
from syntrend.config.model.property_distribution import PropertyDistribution
from syntrend.config.model.enum import DistributionTypes


@dataclass
class PropertyDefinition(Validated):
    """Property Definition

    Definition of how a value is generated and any associated properties to modify its behaviour

    Attributes:
        type (:obj:`str`): Generator Type to be used for this Property Definition
        distribution (:obj:`PropertyDistribution`): Property to define how the generated values will vary using a
            :obj:`DistributionTypes`. Defaults to "none"
        expression (:obj:`str`): String Expression to define a trend, behaviour, or conditions to apply.

            See Also:
                For more information on Expressions, see `Expressions <docs/expressions>`__.
        start: Any value associated with :obj:`type` for when a previous value is expected but none available.
        items (:obj:`list`): List of items required for Generator Types needing a list of objects to choose from.
        properties (:obj:`dict[str, PropertyDefinition]`): Mapping of sub properties namely to support nested objects.
    """

    name: str
    type: str
    distribution: DistributionTypes | PropertyDistribution = dc.field(
        default=DistributionTypes.NoDistribution
    )
    conditions: list[str] = dc.field(default_factory=list)
    expression: str = dc.field(default='')
    start: any = dc.field(default=None)
    hidden: bool = dc.field(default=False)
    items: list[any] = dc.field(default_factory=list)
    properties: dict[str, 'PropertyDefinition'] = dc.field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def parse_distribution(self, dist_type):
        if isinstance(dist_type, str):
            dist_type = DistributionTypes(dist_type)
        if isinstance(dist_type, DistributionTypes):
            dist_type = {'type': dist_type}
        if isinstance(dist_type, dict):
            dist_type = PropertyDistribution(**dist_type)
        return dist_type

    def parse_properties(self, props):
        base_properties = parse_bases(props)
        new_properties = {}

        for prop_name, prop in base_properties.items():
            if isinstance(prop, PropertyDefinition):
                new_properties[prop_name] = prop
                continue
            if not isinstance(prop, dict):
                raise ValueError(
                    '`properties` block was not provided a "Name => Definition" mapping',
                    {
                        'Object': self.name,
                        'Property Name': prop_name,
                        'Property Value': str(prop),
                    },
                )
            new_properties[prop_name] = PropertyDefinition(
                name=prop_name if 'name' not in prop else prop['name'], **prop
            )
        return new_properties
