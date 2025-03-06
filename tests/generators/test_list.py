from syntrend.config import load_config
from syntrend.generators.complex_object import ListGeneratorBase, PropertyGenerator
from syntrend.utils.manager import ROOT_MANAGER

from pytest import mark


def prepare_generator(object_def: dict) -> PropertyGenerator:
    load_config({'simple_list': object_def})
    ROOT_MANAGER.load()
    generator = ROOT_MANAGER.generators['simple_list']
    return generator


@mark.issue(id=18)
@mark.unit
def test_simple_string_list(load_generator):
    generator = load_generator(
        ListGeneratorBase,
        {
            'type': 'list',
            'min_length': 6,
            'max_length': 6,
            'sub_type': {'type': 'string'},
        },
    )
    result = generator.generate()
    assert type(result.visible) is list, 'List Generators should generate a list'
    assert len(result.visible) == 6, 'The list should have 6 elements'
    assert all([type(value) is str for value in result.visible]), (
        'The list should contain all strings'
    )


@mark.issue(id=18)
@mark.unit
def test_simple_number_list(load_generator):
    generator = load_generator(
        ListGeneratorBase,
        {
            'type': 'list',
            'min_length': 6,
            'max_length': 6,
            'sub_type': {'type': 'integer'},
        },
    )
    result = generator.generate()
    assert type(result.visible) is list, 'List Generators should generate a list'
    assert len(result.visible) == 6, 'The list should have 6 elements'
    assert all([type(value) is int for value in result.visible]), (
        'The list should contain all strings'
    )


@mark.issue(id=18)
@mark.unit
def test_simple_incremental_list():
    generator = prepare_generator(
        {'type': 'list', 'sub_type': {'type': 'integer', 'expression': 'kwargs.index'}}
    )
    result = generator.generate()
    current = -1
    for value in result.visible:
        assert value == current + 1, 'Values in list should increment by one'
        current = value


@mark.issue(id=18)
@mark.unit
def test_complex_string_list(load_generator):
    generator = load_generator(
        ListGeneratorBase,
        {
            'type': 'list',
            'sub_type': {'type': 'object', 'properties': {'text': {'type': 'string'}}},
        },
    )
    result = generator.generate()
    previous = ''
    for value in result.visible:
        assert type(value) is dict, 'Values in list should be a dictionary/object'
        assert 'text' in value, 'Value object should contain a "text" property'
        assert type(value['text']) is str, 'Text Value should contain a string'
        assert value['text'] != previous, (
            'Previous "text" value should be unique from other values'
        )


@mark.issue(id=18)
@mark.unit
def test_index_support_from_object():
    generator = prepare_generator(
        {
            'type': 'list',
            'sub_type': {
                'type': 'object',
                'properties': {
                    'index': {'type': 'integer', 'expression': 'kwargs.index'}
                },
            },
        }
    )
    result = generator.generate()
    for index, value in enumerate(result.visible):
        assert value['index'] == index, (
            "`index` value in object should be it's index position in the list"
        )
