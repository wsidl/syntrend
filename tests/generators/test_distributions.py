from event_gen.config import model
from event_gen.generators import distributions as d, generators as g

from functools import partial

from pytest import mark

Prop_Def = partial(model.PropertyDefinition, name_="test")


@mark.parametrize("prop_cfg", [
        [Prop_Def(type="str")],
        [Prop_Def(type="str", distribution=model.DistributionTypes.NoDistribution)],
    ],
    ids=["default_dist", "given_dist"],
)
def test_no_distribution(prop_cfg):
    prop_cfg = Prop_Def(
        type="float",
        distribution=model.DistributionTypes.NoDistribution
    )
    gen_func = g.string_generator
    dist_func = d.get_distribution(prop_cfg, gen_func)
    assert gen_func == dist_func(prop_cfg, gen_func), "The NoDist Generator runs an un-altered function generator"


@mark.parametrize(
    "_type,_type_str,_func,_min,_max",
    [
        [int, "integer", g.integer_generator, 0, 5],
        [float, "float", g.float_generator, 0, 5],
    ]
)
def test_linear_distribution_numeric(_type, _type_str, _func, _min, _max):
    prop_cfg = Prop_Def(
        type=_type_str,
        distribution=model.PropertyDistribution(
            type=model.DistributionTypes.Linear,
            offset_min=0,
            offset_max=5
        )
    )
    gen_func = d.get_distribution(prop_cfg, _func)
    gen_values = [
        gen_func() for _ in range(30)
    ]
    assert all([_min <= x <= _max for x in gen_values]), "All Values must be within the current tolerance"
