from syntrend.generators import integer

from pytest import mark


INT_DEFAULTS = integer.IntegerGenerator.default_config


@mark.unit
def test_default_integer(load_generator):
    generator = load_generator(integer.IntegerGenerator, {'type': 'integer'})
    result = generator.generate()
    assert isinstance(result, int), 'Generated number should be an integer'
    assert INT_DEFAULTS['min_offset'] <= result <= INT_DEFAULTS['max_offset'], (
        'Generated number should be within the default range'
    )


@mark.unit
def test_new_minimum_integer(load_generator):
    generator = load_generator(
        integer.IntegerGenerator, {'type': 'integer', 'min_offset': 100}
    )
    result = generator.generate()
    assert isinstance(result, int), 'Generated number should be an integer'
    assert 100 <= result <= INT_DEFAULTS['max_offset'], (
        'Generated number should be greater than 100'
    )


@mark.unit
def test_new_maximum_integer(load_generator):
    generator = load_generator(
        integer.IntegerGenerator, {'type': 'integer', 'max_offset': -100}
    )
    result = generator.generate()
    assert isinstance(result, int), 'Generated number should be an integer'
    assert INT_DEFAULTS['min_offset'] <= result <= -100, (
        'Generated number should be less than -100'
    )


@mark.unit
def test_set_range_integer(load_generator):
    generator = load_generator(
        integer.IntegerGenerator, {'type': 'integer', 'min_offset': 2, 'max_offset': 3}
    )
    result = generator.generate()
    assert isinstance(result, int), 'Generated number should be an integer'
    assert result in {2, 3}, 'Generated number should be 2 or 3'
