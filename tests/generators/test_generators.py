from syntrend.config import model
import syntrend.generators as generators
import syntrend.generators.string as string_gen

from functools import partial

from pytest import mark, fixture

Prop_Def = partial(model.PropertyDefinition, name="test")


@fixture(scope="function", autouse=True)
def load_generators():
    generators.load_generators()


def test_load_default_generator():
    base_def = Prop_Def(type="string", **generators.GENERATORS["string"].default_config)
    prop_def = Prop_Def(type="string")
    str_gen = generators.get_generator(prop_def, None)
    exp_gen = string_gen.StringGenerator(base_def)
    assert str_gen.__class__ == exp_gen.__class__, "Load Generator should return the String Generator"


@generators.register
class RandomTestGenerator(generators.PropertyGenerator):
    name = "test"

    def generate(self):
        return 1, "test", self.config.kwargs


def test_register_generator():
    prop_def = Prop_Def(type="test")
    exp_gen = RandomTestGenerator(prop_def)
    try:
        test_gen = generators.get_generator(prop_def, None)
    except KeyError:
        raise ValueError("Should have found a 'test' generator")
    assert test_gen.__class__ == exp_gen.__class__, "Should have returned the 'test' generator"
