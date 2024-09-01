from syntrend.config import model

from pytest import mark, raises


@mark.unit
@mark.parametrize('value,_min,_max', [(1, 0, 2), (1, 1, 2), ('2', -2, 2), (-3, -5, -1)])
def test_parse_int(value, _min, _max):
    callback = model.parse_int(_min, _max)
    response = callback(None, value)
    assert response == int(value)


@mark.unit
@mark.parametrize(
    'value,_min,_max,_error_type,_error',
    [
        (0, 1, 2, ValueError, 'Value must be >= 1'),
        (4, 0, 2, ValueError, 'Value must be <= 2'),
        ({}, 4, 2, TypeError, 'Value must be parsable to integer'),
    ],
)
def test_parse_int_errors(value, _min, _max, _error_type, _error):
    callback = model.parse_int(_min, _max)
    with raises(_error_type) as exc:
        callback(None, value)
    assert exc.value.args[0] == _error


@mark.unit
def test_module_config_default():
    cfg = model.ModuleConfig()
    assert cfg.max_generator_retries == 20
    assert cfg.max_historian_buffer == 20
    assert cfg.generator_dir == model.ADD_GENERATOR_DIR


@mark.unit
def test_module_config_max_generator_retries():
    cfg = model.ModuleConfig(**{'max_generator_retries': 10})
    assert cfg.max_generator_retries == 10
    assert cfg.max_historian_buffer == 20
    assert cfg.generator_dir == model.ADD_GENERATOR_DIR


@mark.unit
def test_module_config_max_historian_buffer():
    cfg = model.ModuleConfig(**{'max_historian_buffer': 10})
    assert cfg.max_generator_retries == 20
    assert cfg.max_historian_buffer == 10
    assert cfg.generator_dir == model.ADD_GENERATOR_DIR


@mark.unit
def test_module_config_generator_dir():
    cfg = model.ModuleConfig(**{'max_historian_buffer': 10})
    assert cfg.max_generator_retries == 20
    assert cfg.max_historian_buffer == 10
    assert cfg.generator_dir == model.ADD_GENERATOR_DIR


@mark.unit
def test_module_config_bad_dir():
    with raises(ValueError):
        model.ModuleConfig(generator_dir='not_real')


@mark.unit
def test_project_config_invalid_type():
    with raises(TypeError) as exc:
        model.ModuleConfig(max_generator_retries=[])
    assert (
        exc.value.args[0] == 'Value must be parsable to integer'
    ), 'TypeError message should match output from module'
