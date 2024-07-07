from event_gen.config import model
from event_gen.generators import distributions as d, generators as g

from functools import partial

from pytest import mark, raises

Prop_Def = partial(model.PropertyDefinition, name="test")


@mark.parametrize("prop_cfg", [
        Prop_Def(type="string"),
        Prop_Def(type="string", distribution=model.DistributionTypes.NoDistribution),
    ],
    ids=["default_dist", "given_dist"],
)
def test_no_distribution(prop_cfg):
    gen_func = g.load_generator(prop_cfg)
    dist_func = d.get_distribution(prop_cfg, gen_func)
    assert gen_func == dist_func, "The NoDist Generator runs an un-altered function generator"


@mark.parametrize("_type,_type_str", [[int, "integer"], [float, "float"]])
def test_linear_distribution_numeric(_type: type, _type_str: str):
    prop_cfg = Prop_Def(
        type=_type_str,
        distribution=model.PropertyDistribution(
            type=model.DistributionTypes.Linear,
            min_offset=0,
            max_offset=5
        ),
        min_offset=0,
        max_offset=5
    )
    gen_func = g.load_generator(prop_cfg)
    dist_func = d.get_distribution(prop_cfg, gen_func)
    gen_values = [
        dist_func() for _ in range(30)
    ]
    assert all([0 <= x <= 10 for x in gen_values]), "All Values must be within the current tolerance"


@mark.parametrize("_type,_type_str", [[str, "string"], [dict, "object"], [str, "hex"], [str, "uuid"]])
def test_linear_distribution_invalid_type(_type: type, _type_str: str):
    prop_cfg = Prop_Def(type=_type_str, distribution=model.PropertyDistribution(type=model.DistributionTypes.Linear))
    gen_func = g.load_generator(prop_cfg)
    with raises(AssertionError):
        d.get_distribution(prop_cfg, gen_func)
