from syntrend import generators
from syntrend.config import model

from pytest import fixture


@fixture(scope='function', autouse=True)
def load_generators():
    generators.load_generators()


class FakeManager:
    @staticmethod
    def current_iteration(_):
        return 0


@fixture(scope='function')
def manager():
    return FakeManager()


@fixture(scope='function')
def load_generator(manager, monkeypatch):
    def _config(generator_type, config):
        project_config = model.ProjectConfig(**{'objects': {'test': config}})
        monkeypatch.setattr(generators, 'CONFIG', project_config)
        generator = generator_type('test', project_config.objects['test'])
        generator.load(manager)
        return generator

    return _config
