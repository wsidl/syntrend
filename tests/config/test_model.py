from syntrend.config import model

from pytest import mark, raises


@mark.unit
def test_project_config_lower_val():
    with raises(AssertionError) as exc:
        model.ModuleConfig(max_generator_retries=-1)
    assert exc.type == AssertionError, "Calling ModuleConfig with a negative integer should raise an AssertionError"
    assert exc.value.args[0] == "Value must be >= 1", "Exception raised should say the value must be >= 1"


@mark.unit
def test_project_config_invalid_type():
    with raises(TypeError) as exc:
        model.ModuleConfig(max_generator_retries=[])
    assert exc.type is TypeError, "Expecting TypeError for value type mismatch"
    assert exc.value.args[0] == "Value must parsable to integer", "TypeError message should match output from module"
