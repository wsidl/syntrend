from syntrend.config import model, CONFIG
from syntrend.generators import generators, historian
from syntrend.utils import formatters

from jinja2 import Environment, BaseLoader

from time import time, sleep
import re

RE_EXPR_TOKEN = re.compile(r"\{([^}]+)}")


def load_object_generator(object_name: str):
    object_def = CONFIG.objects[object_name]
    property_def = object_def.into__(model.PropertyDefinition)
    object_gen = generators.load_generator(property_def)
    formatter = formatters.load_formatter(object_name, object_def.output)

    def _generate():
        value = object_gen()
        formatter(value)
        return value

    return _generate


class SeriesManager:
    def __init__(self):
        self.__object_generators = {}
        self.__historians: dict[str, historian.Historian] = {}

    def load(self):
        _deps = []

        def _parse_prop(prop_name: str, cfg: model.PropertyDefinition):
            key = prop_name
            _key_deps = []
            if cfg.expression and isinstance(cfg.expression, str):
                for token in RE_EXPR_TOKEN.finditer(cfg.expression):
                    _deps.append(())

        for obj_name in CONFIG.objects:
            _parse_prop("", CONFIG.objects[obj_name])

    def start(self):
        for obj_name in CONFIG.objects:
            self.__object_generators[obj_name] = load_object_generator(obj_name)
            self.__historians[obj_name] = historian.Historian()

        def _run(_obj_name: str):
            value = self.__object_generators[_obj_name]()
            self.__historians[_obj_name].append(value)

        for obj_name in CONFIG.objects:
            for _ in range(CONFIG.objects[obj_name].output.record_count):
                _run(obj_name)
                # sleep(1)


ROOT_MANAGER = SeriesManager()
