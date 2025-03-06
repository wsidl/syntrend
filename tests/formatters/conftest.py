from syntrend.config import model
from pytest import fixture


@fixture(scope='function')
def patch_formatter(monkeypatch):
    def _config(module, config):
        project_config = model.ProjectConfig(**{'objects': {'test': config}})
        monkeypatch.setattr(module, 'CONFIG', project_config)

    return _config
