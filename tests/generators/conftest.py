from syntrend import generators

from pytest import fixture


@fixture(scope='function', autouse=True)
def load_generators():
    generators.load_generators()
