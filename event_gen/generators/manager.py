from event_gen.config import model, CONFIG
from event_gen.generators import generators, historian
from event_gen.utils import formatters

from jinja2 import Environment, BaseLoader

from time import time, sleep


def load_object_generator(object_name: str):
    object_def = CONFIG.objects[object_name]
    property_def = object_def.into__(model.PropertyDefinition)
    object_gen = generators.load_generator(property_def.type, ROOT_MANAGER, property_def)
    formatter = formatters.load_formatter(object_name, object_def.output)

    def _generate():
        value = object_gen()
        formatter(value)

    return _generate


class SeriesManager:
    def __init__(self):
        self.__object_generators = {}

    def start(self):
        def _run(_obj_name: str):
            self.__object_generators[_obj_name]()

        for obj_name in CONFIG.objects:
            self.__object_generators[obj_name] = load_object_generator(obj_name)

        for obj_name in CONFIG.objects:
            for _ in range(CONFIG.objects[obj_name].output.record_count):
                _run(obj_name)
                sleep(1)


ROOT_MANAGER = SeriesManager()
