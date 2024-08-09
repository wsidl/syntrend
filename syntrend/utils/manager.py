from syntrend.config import model, CONFIG
from syntrend.generators import get_generator
from syntrend.utils import formatters, historian, filters

from jinja2 import Environment, BaseLoader

import re

RE_EXPR_TOKEN = re.compile(r"\{([^}]+)}")


class DependencySet(set[str]):
    @classmethod
    def from_set(cls, other):
        return DependencySet(other)


class CircularDependencySet(DependencySet):
    pass


def load_object_generator(object_name: str):
    object_def = CONFIG.objects[object_name]
    property_def = object_def.into__(model.PropertyDefinition)
    object_gen = get_generator(property_def, ROOT_MANAGER)
    formatter = formatters.load_formatter(object_name, object_def.output)

    def _generate():
        value = object_gen.compile()
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


def prepare_dependency_tree(dependencies: dict[str, set[str]]) -> list[DependencySet]:
    dependency_tree = []
    deps = dependencies.copy()
    all_branches = set(deps.keys())
    while deps:
        leaf_nodes = set(
            _value
            for _value_set in deps.values()
            for _value in _value_set
        ) - set(deps.keys())
        leaf_nodes.update(leaf_key for leaf_key, leaf_value in deps.items() if not leaf_value)
        missing_leaves = leaf_nodes - all_branches
        if missing_leaves:
            raise ValueError(f"Missing leaf nodes: {', '.join(missing_leaves)}")
        if leaf_nodes:
            dependency_tree.append(DependencySet.from_set(leaf_nodes))
            deps = dict(((key, value_set - leaf_nodes) for key, value_set in deps.items() if value_set))
        else:
            # Circular Dependency
            for circ_ref in evaluate_circular_dependencies(deps):
                dependency_tree.append(CircularDependencySet.from_set(circ_ref))
                for key in circ_ref:
                    deps.pop(key, None)
    return dependency_tree


def iter_property_dependencies(parent_key: str, cfg: model.PropertyDefinition) -> dict[str, set[str]]:
    sub_keys = {parent_key: set()}
    if cfg.expression and isinstance(cfg.expression, str):
        for token in RE_EXPR_TOKEN.finditer(cfg.expression):
            sub_keys[parent_key].add(token.group(1))

    for condition in cfg.conditions or []:
        for token in RE_EXPR_TOKEN.finditer(condition):
            sub_keys[parent_key].add(token.group(1))

    for idx, item in enumerate(cfg.items):
        if isinstance(item, str):
            continue
        sub_keys.update(iter_property_dependencies(f"{parent_key}[{idx}]", item))
    for key in cfg.properties:
        sub_keys.update(iter_property_dependencies(f"{parent_key}.{key}", cfg.properties[key]))

    return sub_keys


class SeriesManager:
    def __init__(self):
        self.__object_generators = {}
        self.historians: dict[str, historian.Historian] = {}
        self.__dependency_paths: dict[str, set[str]] = {}
        self.__dependency_order: list[DependencySet] = []
        self.expression_env = Environment(loader=BaseLoader())

    def load_expression(self, expression: str):
        compiled_expr = self.expression_env.compile_expression(expression, undefined_to_none=False)

        def _generate(**kwargs):
            try:
                return compiled_expr(**(self.historians | kwargs))
            except IndexError:
                return

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
            value = self.__object_generators[_obj_name]()
            self.historians[_obj_name].append(value)

        for obj_name in CONFIG.objects:
            for _ in range(CONFIG.objects[obj_name].output.count):
                _run(obj_name)
                # sleep(1)


ROOT_MANAGER = SeriesManager()
