from syntrend.config import CONFIG
from syntrend.generators import get_generator, PropertyGenerator, RenderValue
from syntrend.utils import historian, filters
from syntrend.formatters import load_formatter

from jinja2 import Environment, BaseLoader, exceptions

import re
import time
from datetime import datetime

RE_EXPR_PATH_FUNC = re.compile(r"path\(['\"](.*?)['\"]\)")


class SeriesManager:
    def __init__(self):
        self.generators = {}
        self.formatters = {}
        self.historians: dict[str, historian.Historian] = {}
        self.expression_env = Environment(loader=BaseLoader())
        self.__renderers: dict[str, int] = {}
        self.__expr_lookups = {}

    def current_iteration(self, object_name: str) -> int:
        return self.__renderers[object_name]

    def load_expression(self, prop_generator: PropertyGenerator):
        compiled_expr = self.expression_env.compile_expression(
            prop_generator.config.expression, undefined_to_none=False
        )

        def _generate(**kwargs):
            try:
                return compiled_expr(**kwargs)
            except exceptions.UndefinedError as e:
                field = e.args[0].split(' ')[0][1:-1]
                raise ValueError(
                    'Reference field is not defined',
                    {
                        'Property': prop_generator.config.name,
                        'Missing Field': field,
                    },
                ) from None
            except exceptions.TemplateError as e:
                raise ValueError('Expression failed to execute', *e.args) from None

        return _generate

    def load(self):
        for obj_name in CONFIG.objects:
            self.historians[obj_name] = historian.Historian()
            self.generators[obj_name] = get_generator(
                obj_name, CONFIG.objects[obj_name], ROOT_MANAGER
            )
            self.formatters[obj_name] = load_formatter(obj_name)
            self.__renderers[obj_name] = 0

        filters.load_environment(self)

    def start(self):
        next_events: dict[int, list[tuple[str, RenderValue]]] = {}

        def _run(_obj_name: str):
            rendered_value: RenderValue = self.generators[_obj_name].render()
            if rendered_value.visible:
                self.formatters[_obj_name].format(rendered_value.visible)
            self.historians[_obj_name].append(rendered_value.hidden)

        def _get_next_event(_obj_name: str, _current_time: int):
            if self.__renderers[_obj_name] == CONFIG.objects[_obj_name].output.count:
                return True
            rendered_value: RenderValue = self.generators[_obj_name].render()
            time_value = rendered_value.hidden[
                CONFIG.objects[_obj_name].output.time_field
            ]
            if isinstance(time_value, datetime):
                time_value = time_value.timestamp()
            if _current_time and time_value <= _current_time:
                self.generators[_obj_name].undo()
                return False
            if time_value not in next_events:
                next_events[time_value] = []
            next_events[time_value].append((_obj_name, rendered_value))
            self.__renderers[_obj_name] += 1
            return True

        collection_objects = [
            obj_name
            for obj_name in CONFIG.objects
            if CONFIG.objects[obj_name].output.collection
        ]
        event_objects = [
            obj_name
            for obj_name in CONFIG.objects
            if not CONFIG.objects[obj_name].output.collection
        ]
        time_objects = [
            obj_name
            for obj_name in event_objects
            if CONFIG.objects[obj_name].output.time_field
        ]
        non_time_objects = [
            obj_name for obj_name in event_objects if obj_name not in time_objects
        ]

        # Render collections for references
        for obj_name in collection_objects:
            for iteration in range(CONFIG.objects[obj_name].output.count):
                self.__renderers[obj_name] = iteration
                _run(obj_name)
            self.formatters[obj_name].close()

        # Render events
        for obj_name in non_time_objects:
            for iteration in range(CONFIG.objects[obj_name].output.count):
                self.__renderers[obj_name] = iteration
                _run(obj_name)
            self.formatters[obj_name].close()

        for obj_name in time_objects:
            _get_next_event(obj_name, 0)

        if len(next_events) == 0:
            return
        current_time = min(list(next_events))
        start = time.time()
        while len(next_events) > 0:
            new_time = min(list(next_events))
            if new_time != current_time:
                time.sleep(new_time - current_time - (time.time() - start))
            start = time.time()
            for obj_name, value in next_events.pop(new_time):
                if value.visible:
                    self.formatters[obj_name].format(value.visible)
                self.historians[obj_name].append(value.hidden)
                failed_count = 0
                while _get_next_event(obj_name, new_time) is False:
                    failed_count += 1
                    if failed_count == CONFIG.config.max_generator_retries:
                        raise ValueError(
                            'Failed to generate an event with a later timestamp'
                        )
            current_time = new_time

        # Close Renderers
        for obj_name in time_objects:
            self.formatters[obj_name].close()


ROOT_MANAGER = SeriesManager()
