from syntrend.config import model
from syntrend.utils import generator

from pytest import mark, param, raises


def test_project_config_lower_val():
    with raises(AssertionError) as exc:
        model.ModuleConfig(max_generator_retries=-1)
    assert exc.type == AssertionError, "Calling ModuleConfig with a negative integer should raise an AssertionError"
    assert exc.value.args[0] == "Value must be >= 1", "Exception raised should say the value must be >= 1"


def test_project_config_invalid_type():
    with raises(TypeError) as exc:
        model.ModuleConfig(max_generator_retries=[])
    assert exc.type is TypeError, "Expecting TypeError for value type mismatch"
    assert exc.value.args[0] == "Value must parsable to integer", "TypeError message should match output from module"


# @mark.parametrize(
#     "params,factor,distribution",
#     [
#         param(
#             {"min": -5, "max": 4}, 0, model.DistributionTypes.Linear, id="linear"
#         ),
#         param(
#             {"min": 20, "max": 30, "distribution": "stdDev:20", "trend": "random"},
#             20.0,
#             model.DistributionTypes.StdDev,
#             id="stddev",
#         ),
#     ],
# )
# def test_value_range(
#     params: dict, factor: float, distribution: model.DistributionTypes
# ):
#     new_object = model.ValueRange(**params)
#     assert new_object.distribution == distribution
#     assert new_object.factor == factor
#
#
# def test_value_range_bad_factor():
#     try:
#         generator.ValueRange(
#             **{"min": -5, "max": 4, "distribution": "linear:bad", "trend": "random"}
#         )
#         raise AssertionError("Call should have failed on a bad factor type")
#     except ValidationError:
#         pass

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
