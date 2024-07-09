from syntrend.config import model, CONFIG
from syntrend.generators import get_generator
from syntrend.utils import formatters, historian

from jinja2 import Environment, BaseLoader

from typing import Union
from time import time, sleep
import re

RE_EXPR_TOKEN = re.compile(r"\{([^}]+)}")


def load_object_generator(object_name: str):
    object_def = CONFIG.objects[object_name]
    property_def = object_def.into__(model.PropertyDefinition)
    object_gen = get_generator(property_def)
    formatter = formatters.load_formatter(object_name, object_def.output)

    def _generate():
        value = object_gen.generate()
        formatter(value)
        return value

    return _generate


def evaluate_circular_dependencies(dependencies: dict[str, set[str]]) -> list[list[str]]:
    circular_keys: list[list[str]] = []
    list_deps = {key: list(dependencies[key]) for key in sorted(dependencies)}
    count = 0
    remaining_keys = set(list_deps)
    while remaining_keys:
        count += 1
        if count == 20:
            raise KeyError()
        start_key = sorted(list(remaining_keys))[0]

        def iter_circular(key, key_set):
            for sub_key in list_deps[key]:
                if sub_key == key_set[0]:
                    yield key_set
                if sub_key in key_set:
                    continue
                key_sets = [(len(_set), (_set[0], _set[-1]), _set) for _set in iter_circular(sub_key, key_set + [sub_key])]
                for s_sz, s_ends, s_set in key_sets:
                    if any([s_sz > o_sz and s_ends == o_ends for o_sz, o_ends, _ in key_sets]):
                        continue
                    yield s_set

        circular_keys += [val for val in iter_circular(start_key, [start_key])]
        remaining_keys -= set([key for group in circular_keys for key in group])
    return circular_keys


def prepare_dependency_tree(dependencies: dict[str, set[str]]) -> list[set[str]]:
    dependency_tree = []
    all_branches = set(dependencies.keys())
    while dependencies:
        leaf_nodes = set(
            _value
            for _value_set in dependencies.values()
            for _value in _value_set
        ) - set(dependencies.keys())
        leaf_nodes.update(leaf_key for leaf_key, leaf_value in dependencies.items() if not leaf_value)
        if not leaf_nodes:
            # Circular Dependency
            circular_keys = evaluate_circular_dependencies(dependencies)
            raise ValueError(f"Circular dependency with {', '.join(dependencies.keys())}", circular_keys)
        missing_leaves = leaf_nodes - all_branches
        if missing_leaves:
            raise ValueError(f"Missing leaf nodes: {', '.join(missing_leaves)}")
        dependency_tree.append(leaf_nodes)
        dependencies = dict(((key, value_set - leaf_nodes) for key, value_set in dependencies.items() if value_set))
    return dependency_tree


def parse_expression_dependencies():
    dependencies: dict[str, set[str]] = {}

    def _load_prop(parent_key: str, cfg: model.PropertyDefinition) -> dict[str, set[str]]:
        sub_keys = {parent_key: set()}
        if cfg.expression and isinstance(cfg.expression, str):
            for token in RE_EXPR_TOKEN.finditer(cfg.expression):
                sub_keys[parent_key].add(token.group(1))

        for idx, item in enumerate(cfg.items):
            sub_keys.update(_load_prop(f"{parent_key}[{item}]", cfg.items[item]))
        for key in cfg.properties:
            sub_keys.update(_load_prop(f"{parent_key}.{key}", cfg.properties[key]))

        return sub_keys

    for obj_name in CONFIG.objects:
        for _prop_path, _dep_path in _load_prop(obj_name, CONFIG.objects[obj_name]):
            if _prop_path not in dependencies:
                dependencies[_prop_path] = set()
            dependencies[_prop_path].add(_dep_path)

    return prepare_dependency_tree(dependencies)


class SeriesManager:
    def __init__(self):
        self.__object_generators = {}
        self.__historians: dict[str, historian.Historian] = {}

    def load(self):
        parse_expression_dependencies(CONFIG)

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
