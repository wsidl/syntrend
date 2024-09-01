from syntrend.config import model
from syntrend.utils import distributions as d, manager as m

from functools import partial

from pytest import mark, fixture

Prop_Def = partial(model.PropertyDefinition, name="test")


@fixture(scope="function")
def manager():
    mgr = m.SeriesManager()
    mgr.load()
    return mgr


@mark.unit
@mark.parametrize("prop_cfg", [
        {"type": "string"},
        {"type": "string", "distribution": model.DistributionTypes.NoDistribution},
    ],
    ids=["default_dist", "given_dist"],
)
def test_no_distribution(prop_cfg):
    prop_cfg = Prop_Def(**prop_cfg)
    dist_func = d.get_distribution(prop_cfg.distribution)
    assert "x" == dist_func("x"), "The NoDist Generator returns the value it provides"


@mark.unit
@mark.parametrize("_type_str", [["integer"], ["float"]])
def test_linear_distribution_numeric(_type_str: str):
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
    dist_func = d.get_distribution(prop_cfg.distribution)
    gen_values = [
        dist_func(5) for _ in range(30)
    ]
    assert all([0 <= x <= 10 for x in gen_values]), "All Values must be within the current tolerance"


@mark.unit
@mark.parametrize(
    "std_dev_factor", [0.2, 0.5, 1., 2., 5.]
)
def test_std_dev_distribution(std_dev_factor):
    prop_cfg = Prop_Def(
        type="float",
        distribution=model.PropertyDistribution(
            type=model.DistributionTypes.StdDev,
            std_dev_factor=std_dev_factor
        ),
    )
    offset = std_dev_factor * 6
    dist_func = d.get_distribution(prop_cfg.distribution)
    gen_values = [
        dist_func(5) for _ in range(1000)
    ]
    assert \
        min(gen_values) > 5 - offset and max(gen_values) < 5 + offset, \
        "All Values must be within the current tolerance"
