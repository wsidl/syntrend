from event_gen.config import model
from event_gen.utils import generator

from pydantic import ValidationError
from pytest import mark, param


def test_project_config_lower_val():
    try:
        model.ModuleConfig(max_generator_retries=-1)
        raise AssertionError("ProjectConfig model should raise an error on invalid value")
    except ValidationError as e:
        errors = e.errors()
        assert len(errors) == 1, "A single error is meant to be raised"
        err = errors[0]
        assert err["type"] == "greater_than", "Error should be for invalid integer value"
        assert err["loc"][0] == "max_generator_retries", "Error related to 'max_generator_retries"


def test_project_config_invalid_type():
    try:
        model.ModuleConfig(max_generator_retries=[])
        raise AssertionError("ProjectConfig model should raise an error on invalid value type")
    except ValidationError as e:
        errors = e.errors()
        assert len(errors) == 1, "A single error is meant to be raised"
        err = errors[0]
        assert err["type"] == "int_type", "Error should be for invalid value type"
        assert err["loc"][0] == "max_generator_retries", "Error related to 'max_generator_retries"


@mark.parametrize(
    "params,factor,distribution",
    [
        param(
            {"min": -5, "max": 4}, 0, model.DistributionTypes.Linear, id="linear"
        ),
        param(
            {"min": 20, "max": 30, "distribution": "stdDev:20", "trend": "random"},
            20.0,
            model.DistributionTypes.StdDev,
            id="stddev",
        ),
    ],
)
def test_value_range(
    params: dict, factor: float, distribution: model.DistributionTypes
):
    new_object = model.ValueRange(**params)
    assert new_object.distribution == distribution
    assert new_object.factor == factor


def test_value_range_bad_factor():
    try:
        generator.ValueRange(
            **{"min": -5, "max": 4, "distribution": "linear:bad", "trend": "random"}
        )
        raise AssertionError("Call should have failed on a bad factor type")
    except ValidationError:
        pass

# def test_series_simple_generator():
#     simple_series = model.Project(objects={
#         "simple": model.ObjectConfig(
#             schema="tests/assets/simple_config.json",
#             properties={
#                 "timestamp": generator.PropertyGenerator(
#                     start=946713600, trend="self + 5", value_range=generator.ValueRange(min=4, max=10),
#                     conditions=["simple.timestamp[-1] + 13 > simple.timestamp"]
#                 ),
#                 "status": generator.PropertyGenerator(start="START")
#             }
#         )
#     })
#     print(simple_series)
