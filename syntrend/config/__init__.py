from syntrend.config.model import ProjectConfig
from syntrend.config.parse import load_config as _load_config

CONFIG = ProjectConfig(objects={"self": {"type": "integer"}})


def load_config(config_file):
    _cfg = _load_config(config_file)
    CONFIG.objects = _cfg.objects
    CONFIG.config = _cfg.config

    for obj_name in CONFIG.objects:
        _output = CONFIG.output.copy__()
        _output.update__(CONFIG.objects[obj_name].output)
        CONFIG.objects[obj_name].output = _output


__all__ = [
    ProjectConfig,
    load_config,
]
