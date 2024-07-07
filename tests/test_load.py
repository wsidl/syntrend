from syntrend.config import model
from syntrend import load
from syntrend.utils import generator

from pytest import mark


@mark.parametrize("fields,expected", [
    [{"max_generator_retries": 2}, [2, 20]],
    [{"max_historian_buffer": 2}, [20, 2]],
    [{"max_generator_retries": 2, "max_historian_buffer": 2}, [2, 2]]
])
def test_project_config_generator_retries(monkeypatch, fields, expected):
    monkeypatch.setattr(generator, "MAX_GENERATOR_RETRIES", 20)
    monkeypatch.setattr(generator, "MAX_HISTORIAN_BUFFER", 20)

    project_config = model.ModuleConfig(**fields)
    load.update_module_config(project_config)
    assert (
        generator.MAX_GENERATOR_RETRIES == expected[0]
    ), "Applying the MAX_GENERATOR_RETRIES config should update the global value"
    assert (
        generator.MAX_HISTORIAN_BUFFER == expected[1]
    ), "Applying the MAX_HISTORIAN_BUFFER config should update the global value"


# def test_project_loader():
#     value = load.load_project({"objects": {"simple": {
#         "timestamp": {
#             "start": 946713600,
#             "trend": "self + 5",
#             "value_range": {"min": 4, "max": 10},
#             "conditions": ["simple.timestamp[-1] + 13 > simple.timestamp"],
#         },
#         "status": {"start": "START"}
#     }}})
#     print(value)

    # simple_series = config.SeriesConfig(objects={
    #     "simple": config.ObjectDef(
    #         schema="tests/assets/simple_config.json",
    #         properties={
    #             "timestamp": generator.PropertyGenerator(
    #                 start=946713600, trend="self + 5", value_range=generator.ValueRange(min=4, max=10),
    #                 conditions=["simple.timestamp[-1] + 13 > simple.timestamp"]
    #             ),
    #             "status": generator.PropertyGenerator(start="START")
    #         }
    #     )
    # })
    # print(simple_series)
