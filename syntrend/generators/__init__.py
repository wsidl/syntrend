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


class RenderValue:
    def __init__(self, visible, hidden):
        self.visible = visible
        self.hidden = hidden


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
        new_config = model.PropertyDefinition(
            name=config.name, type=config.type, **self.default_config
        )
        model.update(new_config, config)
        self.config = new_config
        self.properties: dict[str, any] = {}
        self.items: list[any] = []
        self.expression: Callable = default_generator
        self.__expression_loaded: bool = False
        self.start = None
        self.__distribution = None

        kwargs_names = list(self.config.kwargs)
        __modules_nt_type = namedtuple('RequiredModules', self.required_modules)
        __kwargs_nt_type = namedtuple(self.name, kwargs_names)
        self.modules: __modules_nt_type = __modules_nt_type(*self.required_modules)
        self.kwargs: __kwargs_nt_type = __kwargs_nt_type(**self.config.kwargs)
        self.root_manager = None
        self.iteration = -1
        self.iteration_value: RenderValue = RenderValue(..., ...)
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

    def load_items(self, items: list[any]) -> list[any]:
        return items

    def load_properties(self, properties: dict[str, any]) -> dict[str, any]:
        return properties

    def load_kwargs(self, kwargs: dict[str, any]) -> dict[str, any]:
        return kwargs

    def validate(self):
        pass

    def render(self, force=False, **kwargs) -> RenderValue:
        iteration = self.root_manager.current_iteration(self.root_object)
        if self.iteration == iteration and not force:
            return self.iteration_value

        self.iteration = iteration
        if not iteration and self.start is not None:
            self.iteration_value = RenderValue(
                ... if self.config.hidden else self.start, self.start
            )
            return self.iteration_value

        if not isinstance(generated := self.generate(**kwargs), RenderValue):
            generated = RenderValue(... if self.config.hidden else generated, generated)
        if (
            not self.__expression_loaded
            and self.config.expression
            and isinstance(self.config.expression, str)
        ):
            self.expression = self.root_manager.load_expression(self)
        if self.expression != default_generator:
            try:
                calculated = self.expression(
                    new=generated.hidden,
                    interval=self.iteration,
                    kwargs=self.kwargs._asdict() | kwargs,
                )
                generated.hidden = calculated
                if not self.config.hidden:
                    generated.visible = calculated
                self.iteration_value = generated
            except (ValueError, TypeError) as e:
                print(e)
                print(self.name, self.root_object)
                e.args = {
                    'Generator': self.name,
                    'Property': self.root_object,
                    'Expression': self.config.expression,
                }
                exc.process_exception(e)
        else:
            self.iteration_value = generated
        self.iteration_value.hidden = self.__distribution(self.iteration_value.hidden)
        if (
            self.type is not None
            and not isinstance(self.iteration_value.visible, self.type)
            and self.iteration_value.hidden is not ...
        ):
            if self.iteration_value.visible is not ...:
                self.iteration_value.visible = self.type(self.iteration_value.visible)
            self.iteration_value.hidden = self.type(self.iteration_value.hidden)
        return self.iteration_value

    def undo(self):
        self.iteration -= 1

    def generate(self, **kwargs):
        raise NotImplementedError('Generator has not implemented `generate` method')


def register(property_generator: Type[PropertyGenerator]):
    assert property_generator.name, 'Property Generator must have a name specified'
    assert property_generator.name not in GENERATORS, (
        f"Property Generator '{property_generator.name}' already registered"
    )
    GENERATORS[property_generator.name] = load_type(property_generator)
    return property_generator


def get_generator(
    object_name: str, config: model.PropertyDefinition, manager
) -> PropertyGenerator:
    prop_gen_cls = GENERATORS[config.type]
    new_gen = prop_gen_cls(object_name, config)
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
    if not CONFIG.config.generator_dir:
        return
    add_generator_pkg = Path(CONFIG.config.generator_dir).absolute()
    if not (add_generator_pkg.is_dir() and add_generator_pkg.exists()):
        return
    import sys

    generator_pkg_name = add_generator_pkg.name
    sys.path.append(str(add_generator_pkg))
    _load_generator_dir(generator_pkg_name, add_generator_pkg)
