from syntrend.config import model, CONFIG
from syntrend.utils import distributions, exc
from typing import Type, Callable
from pathlib import Path
from importlib import import_module
from collections import namedtuple
import logging

from syntrend.generators.__base_types import load_type

LOG = logging.getLogger(__name__)
GENERATORS: dict[str, Type['PropertyGenerator']] = {}


def default_generator(new, **kwargs):
    return new


class PropertyGenerator:
    """Base Property Generator for all generators

    Keyword Args:
        type (:obj:`str`): Defines the generator to use. See sections below for options
        start: A Starting Value of any type. Necessary if building an expression using a previous value.
        expression (:obj:`str`): Parsable expression (using `Jinja <https://jinja.palletsprojects.com/en/3.1.x/>`__) used to generate expected values. More information in `Expressions Doc </expressions>`__)
    """
    type: Type = None
    name: str = ''
    default_config: dict[str, any] = {}
    required_modules: list[str] = []

    def __init__(self, object_name: str, config: model.PropertyDefinition):
        self.root_object = object_name
        self.config = config
        self.properties: dict[str, any] = {}
        self.items: list[any] = []
        self.expression: Callable = default_generator
        self.start = None
        self.__distribution = None

        kwargs_names = list(self.config.kwargs)
        __modules_nt_type = namedtuple('RequiredModules', self.required_modules)
        __kwargs_nt_type = namedtuple(self.name, kwargs_names)
        self.modules: __modules_nt_type = __modules_nt_type(*self.required_modules)
        self.kwargs: __kwargs_nt_type = __kwargs_nt_type(**self.config.kwargs)
        self.root_manager = None
        self.iteration = -1
        self.iteration_value = None
        self.__modules_nt_type = __modules_nt_type
        self.__kwargs_nt_type = __kwargs_nt_type

    def __repr__(self):
        return f'<{self.__class__.__name__}: current={self.iteration_value}>'

    def load(self, manager):
        self.root_manager = manager
        self.modules = self.__modules_nt_type(
            **{mod_name: import_module(mod_name) for mod_name in self.required_modules}
        )
        kwargs = self.load_kwargs(self.config.kwargs)
        kwargs_tpl = namedtuple(self.name, list(kwargs))
        self.start = self.config.start
        self.kwargs = kwargs_tpl(**kwargs)
        self.properties = self.load_properties(self.config.properties)
        self.items = self.load_items(self.config.items)
        self.validate()
        self.__distribution = distributions.get_distribution(self.config.distribution)
        if self.config.expression and isinstance(self.config.expression, str):
            self.expression = manager.load_expression(self)

    def load_items(self, items: list[any]) -> list[any]:
        return items

    def load_properties(self, properties: dict[str, any]) -> dict[str, any]:
        return properties

    def load_kwargs(self, kwargs: dict[str, any]) -> dict[str, any]:
        return kwargs

    def validate(self):
        pass

    def render(self):
        iteration = self.root_manager.current_iteration(self.root_object)
        if self.iteration == iteration:
            return self.iteration_value

        self.iteration = iteration
        if not iteration and self.start is not None:
            self.iteration_value = self.start
            return self.start

        generated = self.generate()
        try:
            self.iteration_value = self.expression(
                new=generated, interval=self.iteration, kwargs=self.kwargs
            )
        except (ValueError, TypeError) as e:
            exc.process_exception(e)
        self.iteration_value = self.__distribution(self.iteration_value)
        if self.type is not None and not isinstance(self.iteration_value, self.type):
            self.iteration_value = self.type(self.iteration_value)
        return self.iteration_value

    def undo(self):
        self.iteration -= 1

    def generate(self):
        raise NotImplementedError('Generator has not implemented `generate` method')


def register(property_generator: Type[PropertyGenerator]):
    assert property_generator.name, 'Property Generator must have a name specified'
    assert property_generator.name not in GENERATORS, (
        f'Property Generator ' f"'{property_generator.name}' " f'already registered'
    )
    GENERATORS[property_generator.name] = load_type(property_generator)
    return property_generator


def get_generator(
    object_name: str, config: model.PropertyDefinition, manager
) -> PropertyGenerator:
    prop_gen_cls = GENERATORS[config.type]
    new_config = model.PropertyDefinition(
        name=config.name, type=config.type, **prop_gen_cls.default_config
    )
    model.update(new_config, config)
    new_gen = prop_gen_cls(object_name, new_config)
    new_gen.load(manager)
    return new_gen


def _load_generator_dir(module_name: str, directory: Path):
    for _file in directory.iterdir():
        if (
            not _file.suffix.startswith('.py')
            or _file.is_dir()
            or _file.name.startswith('_')
        ):
            continue
        basename = _file.name.split('.')[0]
        _ = import_module(f'{module_name}.{basename}')


def load_generators():
    _load_generator_dir('syntrend.generators', Path(__file__).parent)
    add_generator_pkg = Path(CONFIG.config.generator_dir).absolute()
    if not (add_generator_pkg.is_dir() and add_generator_pkg.exists()):
        return
    import sys

    generator_pkg_name = add_generator_pkg.name
    sys.path.append(str(add_generator_pkg))
    _load_generator_dir(generator_pkg_name, add_generator_pkg)
