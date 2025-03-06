from syntrend.config import model
import syntrend.generators as generators
import syntrend.generators.string as string_gen

from functools import partial

from pytest import mark

Prop_Def = partial(model.PropertyDefinition, name='test')


@mark.unit
def test_load_default_generator():
    base_def = Prop_Def(type='string', **generators.GENERATORS['string'].default_config)
    prop_def = Prop_Def(type='string')
    str_gen = generators.get_generator('test', prop_def, None)
    exp_gen = string_gen.StringGenerator('test', base_def)
    assert str_gen.__class__.__name__ == exp_gen.__class__.__name__, (
        'Load Generator should return the String Generator'
    )


@generators.register
class RandomTestGenerator(generators.PropertyGenerator):
    name = 'test'

    def generate(self, **_):
        return 1, 'test', self.config.kwargs


@mark.unit
def test_register_generator():
    prop_def = Prop_Def(type='test')
    exp_gen = RandomTestGenerator('test', prop_def)
    try:
        test_gen = generators.get_generator('test', prop_def, None)
    except KeyError:
        raise ValueError("Should have found a 'test' generator") from None
    assert test_gen.__class__ == exp_gen.__class__, (
        "Should have returned the 'test' generator"
    )


@mark.issue(id=14)
@mark.unit
def test_generator_with_hidden_simple_value(manager):
    prop_def = Prop_Def(type='string', hidden=True)
    generator = generators.get_generator('test', prop_def, manager)
    generate_result = generator.generate()
    assert isinstance(generate_result, str), 'Generator should return a string'
    render_result = generator.render()
    assert isinstance(render_result, generators.RenderValue), (
        'Generator should return a RenderValue'
    )
    assert isinstance(render_result.hidden, str), (
        'Render from Generator should have a string in the hidden Render Value'
    )
    assert render_result.visible is ..., (
        'Render from Generator should have an Ellipsis in the visible Render Value'
    )
