from syntrend.config.model import ProjectConfig, copy, update
from syntrend.config.parse import load_config as _load_config

default_config = {'objects': {'this': {'type': 'integer'}}}
CONFIG = ProjectConfig(**default_config)


def load_config(config_file):
    global CONFIG
    _cfg = _load_config(config_file)
    CONFIG.objects = _cfg.objects
    CONFIG.config = _cfg.config
    CONFIG.output = _cfg.output

    for obj_name in CONFIG.objects:
        _output = copy(CONFIG.output)
        update(_output, CONFIG.objects[obj_name].output)
        CONFIG.objects[obj_name].output = _output


__all__ = [
    ProjectConfig,
    load_config,
]
