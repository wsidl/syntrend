from event_gen.config import model
from event_gen.utils import generator
import logging
from pytest import mark, param
from pydantic import ValidationError

LOG = logging.getLogger(__name__)


@mark.parametrize(
    "start, next_val",
    [
        param("TEST", "TEST", id="Set Value"),
        param(
            "{{datetime(2000, 1, 1, 7, 50) | to_timestamp}}",
            "946741800.0",
            id="Jinja Value Assignment",
        ),
    ],
)
def test_property_generator_single_trend_value(start: str, next_val):
    new_object = generator.PropertyGenerator(model.PropertyConfig(start=start))
    for _ in range(10):
        assert (
            new_object.generate() == next_val
        ), "Value should always be what was provided at the beginning"


def test_property_generator_single_trend_value_with_methods(monkeypatch):
    import datetime

    dt = datetime.datetime(2000, 1, 1, 7, 5, 0)
    ts = str(dt.timestamp())

    class _dt(datetime.datetime):
        @classmethod
        def now(cls, *args, **kwargs):
            return dt

    monkeypatch.setattr(datetime, "datetime", _dt)
    new_object = generator.PropertyGenerator(model.PropertyConfig(start="{{datetime.now() | to_timestamp}}"))
    new_object.init(None)
    value = new_object.generate()
    assert value == str(
        ts
    ), "Value generated to should be able to call methods/properties on global value"


def test_property_generator_with_linear_trend():
    new_object = generator.PropertyGenerator(model.PropertyConfig(start=0, trend="this + 5"))
    expected_value = 0
    for i in range(10):
        new_value = new_object.generate()
        assert (
            new_value == expected_value
        ), "Values should progress linearly on every iteration"
        expected_value = new_value + 5


def test_property_generator_with_exponential_trend():
    new_object = generator.PropertyGenerator(model.PropertyConfig(start=2, trend="(this + 1) ** 2"))
    expected_value = 2
    for i in range(10):
        new_value = new_object.generate()
        assert (
            new_value == expected_value
        ), "Values should progress linearly on every iteration"
        expected_value = (new_value + 1) ** 2


def test_property_generator_trend_with_random():
    new_object = generator.PropertyGenerator(model.PropertyConfig(
        start=20, value_range=model.ValueRange(min=-5, max=10)
    ))
    for _ in range(20):
        assert (
            15 <= new_object.generate() <= 30
        ), "New Values should be within the range provided"


# noinspection DuplicatedCode
def test_property_generator_trend_random_in_normal_distribution():
    new_object = generator.PropertyGenerator(model.PropertyConfig(
        start=20,
        value_range=model.ValueRange(
            min=-10, max=10, distribution=model.DistributionTypes.StdDev, factor=1
        ),
    ))
    values = []
    size = 1000
    for _ in range(size):
        values.append(new_object.generate() - 20)
    mean = sum(values) / size
    offsets = [abs(val - mean) for val in values]
    std_dev = sum(offsets) / size
    std_devs = [[] for _ in range(4)]
    for val in offsets:
        for sd in range(1, 5):
            if val < sd * std_dev:
                std_devs[sd - 1].append(val)
                break
    std_dev_count = [len(group) for group in std_devs]
    LOG.info(
        "Out of %d/%d Values fitting within 4 Std Deviations, Counts per Std Dev: %s",
        sum(std_dev_count),
        size,
        ", ".join([str(a) for a in std_dev_count]),
    )
    std_dev_percent = [len(group) / size * 100 for group in std_devs]
    std_dev_percent = [round(sum(std_dev_percent[: i + 1]), 1) for i in range(4)]
    LOG.info(
        "Percentages of Values within each Standard Deviation: %s",
        ", ".join([f"{i + 1}={std_dev_percent[i]}" for i in range(4)]),
    )
    assert (
        54.2 <= std_dev_percent[0] <= 60.3
    ), "This distribution should have between 55% and 60% of values within 1 Standard Deviation"
    assert (
        86.4 <= std_dev_percent[1] <= 91.7
    ), "This distribution should have between 85% and 90% of values within 2 Standard Deviations"
    assert (
        97.1 <= std_dev_percent[2] <= 99.6
    ), "This distribution should have between 96% and 99% of values within 3 Standard Deviations"
    assert (
        99.3 <= std_dev_percent[3] <= 100.0
    ), "This distribution should have more than 99.8% of all values within 4 Standard Deviations"


# noinspection DuplicatedCode
def test_property_generator_beta_distribution():
    new_object = generator.PropertyGenerator(model.PropertyConfig(
        start=20,
        value_range=model.ValueRange(
            min=-5, max=10, distribution=model.DistributionTypes.StdDev, factor=1
        ),
    ))
    values = []
    size = 1000
    for _ in range(size):
        values.append(new_object.generate() - 20)
    mean = sum(values) / size
    offsets = [val - mean for val in values]
    offsets_min = [-val for val in values if val < 0]
    offsets_max = [val for val in values if val >= 0]
    std_dev_min = abs(sum(offsets_min)) / len(offsets_min)
    std_dev_max = sum(offsets_max) / len(offsets_max)
    std_devs = [[] for _ in range(4)]
    for val in offsets:
        for sd in range(1, 5):
            if val < 0 and abs(val) < sd * std_dev_min:
                std_devs[sd - 1].append(val)
                break
            if 0 <= val < sd * std_dev_max:
                std_devs[sd - 1].append(val)
                break
    std_dev_count = [len(group) for group in std_devs]
    LOG.info(
        "Out of %d/%d Values fitting within 4 Std Deviations, Counts per Std Dev: %s",
        sum(std_dev_count),
        size,
        ", ".join([str(a) for a in std_dev_count]),
    )
    std_dev_percent = [len(group) / size * 100 for group in std_devs]
    std_dev_percent = [round(sum(std_dev_percent[: i + 1]), 1) for i in range(4)]
    LOG.info(
        "Percentages of Values within each Standard Deviation: %s",
        ", ".join([f"{i + 1}={std_dev_percent[i]}" for i in range(4)]),
    )
    assert (
        54.2 <= std_dev_percent[0] <= 60.3
    ), "This distribution should have between 55% and 60% of values within 1 Standard Deviation"
    assert (
        86.6 <= std_dev_percent[1] <= 91.7
    ), "This distribution should have between 85% and 90% of values within 2 Standard Deviations"
    assert (
        97.1 <= std_dev_percent[2] <= 99.6
    ), "This distribution should have between 96% and 99% of values within 3 Standard Deviations"
    assert (
        99.3 <= std_dev_percent[3] <= 100.0
    ), "This distribution should have more than 99.8% of all values within 4 Standard Deviations"


def test_property_generator_fuzzy_linear_shift_trend_with_algorithm():
    new_object = generator.PropertyGenerator(model.PropertyConfig(
        start=0, trend="this + 5", value_range=model.ValueRange(min=-1, max=2)
    ))
    expected_value = 0
    for i in range(10):
        new_value = new_object.generate()
        assert (
            (expected_value - 1) <= new_value <= (expected_value + 2)
        ), "Values should progress linearly from the last value on every iteration"
        expected_value = expected_value + 5


# noinspection DuplicatedCode
def test_property_generator_progressing_trend_normal_distribution():
    new_object = generator.PropertyGenerator(model.PropertyConfig(
        start=20,
        trend="this + 1",
        value_range=model.ValueRange(
            min=-10, max=10, distribution=model.DistributionTypes.StdDev, factor=1
        ),
    ))
    values = []
    size = 1000
    current = new_object.config.start
    for _ in range(size):
        new = new_object.generate()
        values.append(new - current)
        current += 1
    mean = sum(values) / size
    offsets = [abs(val - mean) for val in values]
    std_dev = sum(offsets) / size
    std_devs = [[] for _ in range(4)]
    for val in offsets:
        for sd in range(1, 5):
            if val < sd * std_dev:
                std_devs[sd - 1].append(val)
                break
    std_dev_count = [len(group) for group in std_devs]
    LOG.info(
        "Out of %d/%d Values fitting within 4 Std Deviations, Counts per Std Dev: %s",
        sum(std_dev_count),
        size,
        ", ".join([str(a) for a in std_dev_count]),
    )
    std_dev_percent = [len(group) / size * 100 for group in std_devs]
    std_dev_percent = [round(sum(std_dev_percent[: i + 1]), 1) for i in range(4)]
    LOG.info(
        "Percentages of Values within each Standard Deviation: %s",
        ", ".join([f"{i + 1}={std_dev_percent[i]}" for i in range(4)]),
    )
    assert (
        54.2 <= std_dev_percent[0] <= 60.3
    ), "This distribution should have between 55% and 60% of values within 1 Standard Deviation"
    assert (
        86.6 <= std_dev_percent[1] <= 91.7
    ), "This distribution should have between 85% and 90% of values within 2 Standard Deviations"
    assert (
        97.1 <= std_dev_percent[2] <= 99.6
    ), "This distribution should have between 96% and 99% of values within 3 Standard Deviations"
    assert (
        99.3 <= std_dev_percent[3] <= 100.0
    ), "This distribution should have more than 99.8% of all values within 4 Standard Deviations"


def test_property_generator_fuzzy_linear_shift_trend_from_last_value_with_algorithm():
    new_object = generator.PropertyGenerator(model.PropertyConfig(
        start=0,
        trend="this + 5",
        progression=model.Progress.Last,
        value_range=model.ValueRange(min=-1, max=2),
    ))
    expected_value = 0
    for i in range(10):
        new_value = new_object.generate()
        assert (
            (expected_value - 1) <= new_value <= (expected_value + 2)
        ), "Values should progress linearly from the last value on every iteration"
        expected_value = new_value + 5


# noinspection DuplicatedCode
def test_property_generator_progressing_trend_from_last_value_normal_distribution():
    new_object = generator.PropertyGenerator(model.PropertyConfig(
        start=20,
        trend="this + 1",
        progression=model.Progress.Last,
        value_range=model.ValueRange(
            min=-10, max=10, distribution=model.DistributionTypes.StdDev, factor=1
        ),
    ))
    values = []
    size = 1000
    current = new_object.config.start
    for _ in range(size):
        new = new_object.generate()
        values.append(new - current)
        current = new + 1
    mean = sum(values) / size
    offsets = [abs(val - mean) for val in values]
    std_dev = sum(offsets) / size
    std_devs = [[] for _ in range(4)]
    for val in offsets:
        for sd in range(1, 5):
            if val < sd * std_dev:
                std_devs[sd - 1].append(val)
                break
    std_dev_count = [len(group) for group in std_devs]
    LOG.info(
        "Out of %d/%d Values fitting within 4 Std Deviations, Counts per Std Dev: %s",
        sum(std_dev_count),
        size,
        ", ".join([str(a) for a in std_dev_count]),
    )
    std_dev_percent = [len(group) / size * 100 for group in std_devs]
    std_dev_percent = [round(sum(std_dev_percent[: i + 1]), 1) for i in range(4)]
    LOG.info(
        "Percentages of Values within each Standard Deviation: %s",
        ", ".join([f"{i + 1}={std_dev_percent[i]}" for i in range(4)]),
    )
    assert (
        54.2 <= std_dev_percent[0] <= 60.3
    ), "This distribution should have between 55% and 60% of values within 1 Standard Deviation"
    assert (
        86.6 <= std_dev_percent[1] <= 91.7
    ), "This distribution should have between 85% and 90% of values within 2 Standard Deviations"
    assert (
        97.1 <= std_dev_percent[2] <= 99.6
    ), "This distribution should have between 96% and 99% of values within 3 Standard Deviations"
    assert (
        99.3 <= std_dev_percent[3] <= 100.0
    ), "This distribution should have more than 99.8% of all values within 4 Standard Deviations"


def test_property_generator_historian_parse():
    new_object = generator.PropertyGenerator(model.PropertyConfig(
        start=20,
        value_range=model.ValueRange(min=0, max=1),
        conditions=["20 <= this <= 20.5"],
    ))
    value = new_object.generate()
    assert 20 <= value <= 20.5, "Condition didn't apply reliably"


def test_property_generator_condition_fail(monkeypatch):
    def set_value(_):
        def _return_value(_):
            return 30

        return _return_value

    monkeypatch.setattr("event_gen.utils.generator.MAX_GENERATOR_RETRIES", 5)
    monkeypatch.setattr("event_gen.utils.generator.generator_factory", set_value)
    new_object = generator.PropertyGenerator(model.PropertyConfig(
        start=20,
        value_range=model.ValueRange(min=-10, max=10),
        conditions=["20 <= this <= 20.1"],
    ))
    first_value = new_object.generate()
    assert first_value == 20, "First value should be using the generator's start value"
    error_raised = False
    try:
        new_object.generate()
    except ValueError as e:
        assert e.args[0] == (
            "Generator cannot provide a value that also meets condition requirements. Try adjusting conditions, "
            "range, or trend parameters.\nGenerated values attempted: [30, 30, 30, 30, 30]"
        ), f"ValueError generated, but incorrect message received:\n{e.args[0]}"
        error_raised = True
    except Exception as e:
        raise AssertionError(
            f'Incorrect Exception raised of type "{type(e).__name__}"\n{e.args[0]}'
        )
    if not error_raised:
        raise AssertionError(
            "No error raised during execution. Condition and mock generators are meant to fail"
        )
