from syntrend.config import model
from syntrend import generators

from pytest import mark


@mark.unit
def test_object_generator(manager):
    prop_def = model.PropertyDefinition(
        name='test',
        type='object',
        properties={
            'prop1': model.PropertyDefinition(type='string'),
            'prop2': model.PropertyDefinition(type='string'),
        },
    )
    generator = generators.get_generator('test', prop_def, manager)
    generate_result = generator.generate()
    assert isinstance(generate_result, generators.RenderValue), (
        'Generator should return a dictionary'
    )
    assert isinstance(generate_result.hidden, dict), (
        'Generated result should be a dictionary'
    )
    assert isinstance(generate_result.visible, dict), (
        'Generated result should be a dictionary'
    )
    assert isinstance(generate_result.hidden['prop1'], str), (
        '"prop1" of the hidden object should contain a string'
    )
    assert isinstance(generate_result.hidden['prop2'], str), (
        '"prop2" of the hidden object should contain a string'
    )
    assert isinstance(generate_result.visible['prop1'], str), (
        '"prop1" of the hidden object should contain a string'
    )
    assert isinstance(generate_result.visible['prop2'], str), (
        '"prop2" of the visible object should contain a string'
    )


@mark.issue(id=14)
@mark.unit
def test_generator_with_hidden_object_property(manager):
    prop_def = model.PropertyDefinition(
        name='test',
        type='object',
        properties={
            'prop1': model.PropertyDefinition(type='string', hidden=True),
            'prop2': model.PropertyDefinition(type='string'),
        },
    )
    generator = generators.get_generator('test', prop_def, manager)
    generate_result = generator.generate()
    assert isinstance(generate_result, generators.RenderValue), (
        'Generator should return a dictionary'
    )
    assert isinstance(generate_result.hidden['prop1'], str), (
        '"prop1" of the hidden object should contain a string'
    )
    assert isinstance(generate_result.hidden['prop2'], str), (
        '"prop2" of the hidden object should contain a string'
    )
    assert isinstance(generate_result.visible['prop2'], str), (
        '"prop2" of the visible object should contain a string'
    )
    assert 'prop1' not in generate_result.visible, (
        '"prop1" should not exist in the visible object'
    )
    render_result = generator.render()
    assert isinstance(render_result, generators.RenderValue), (
        'Generator should return a render of RenderValue type'
    )
    assert isinstance(render_result.hidden['prop1'], str), (
        '"prop1" of the hidden object should contain a string'
    )
    assert isinstance(render_result.hidden['prop2'], str), (
        '"prop2" of the hidden object should contain a string'
    )
    assert isinstance(render_result.visible['prop2'], str), (
        '"prop2" of the visible object should contain a string'
    )
    assert 'prop1' not in render_result.visible, (
        '"prop1" should not exist in the visible object'
    )
