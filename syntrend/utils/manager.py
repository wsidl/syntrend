from syntrend.config import model, CONFIG
from syntrend.generators import get_generator, PropertyGenerator
from syntrend.utils import formatters, historian, filters

from jinja2 import Environment, BaseLoader

import re

RE_EXPR_PATH_FUNC = re.compile(r"path\(['\"](.*?)['\"]\)")


class SeriesManager:
    def __init__(self):
        self.generators = {}
        self.formatters = {}
        self.historians: dict[str, historian.Historian] = {}
        self.expression_env = Environment(loader=BaseLoader())
        self.__active_renderer: str = ""
        self.__renderers: dict[str, int] = {}
        self.__expr_lookups = {}

    def renderer(self) -> tuple[str, int]:
        return self.__active_renderer, self.__renderers[self.__active_renderer]

    def load_expression(self, prop_generator: PropertyGenerator):
        compiled_expr = self.expression_env.compile_expression(prop_generator.config.expression, undefined_to_none=False)

        def _generate(**kwargs):
            return compiled_expr(**kwargs)

        return _generate

    def start(self):
        for obj_name in CONFIG.objects:
            self.historians[obj_name] = historian.Historian()
            object_def = CONFIG.objects[obj_name]
            property_def = object_def.into__(model.PropertyDefinition)
            self.generators[obj_name] = get_generator(obj_name, property_def, ROOT_MANAGER)
            self.formatters[obj_name] = formatters.load_formatter(obj_name, object_def.output)
            self.__renderers[obj_name] = 0

        filters.load_environment(self)

        def _run(_obj_name: str):
            value = self.generators[_obj_name].render()
            self.formatters[_obj_name](value)
            self.historians[_obj_name].append(value)

        for obj_name in CONFIG.objects:
            self.__active_renderer = obj_name
            for iteration in range(CONFIG.objects[obj_name].output.count):
                self.__renderers[obj_name] = iteration
                _run(obj_name)


ROOT_MANAGER = SeriesManager()
