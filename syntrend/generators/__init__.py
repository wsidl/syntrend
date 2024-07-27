from syntrend.config import model, CONFIG
from typing import Type, Callable
from pathlib import Path
from importlib import import_module
from collections import namedtuple
from os import getenv
import logging

LOG = logging.getLogger(__name__)
GENERATORS: dict[str, Type["PropertyGenerator"]] = {}


def default_generator(new, **kwargs):
    return new


class PropertyGenerator:
    name: str = ""
    default_config: dict[str, any] = {}
    required_modules: list[str] = []

    def __init__(self, config: model.PropertyDefinition):
        self.config = config
        self.properties: dict[str, any] = {}
        self.items: list[any] = []
        self.expression: Callable = default_generator
        self.start = None

        kwargs_names = list(self.config.kwargs)
        __modules_nt_type = namedtuple("RequiredModules", self.required_modules)
        __kwargs_nt_type = namedtuple(self.name, kwargs_names)
        self.modules: __modules_nt_type = __modules_nt_type(*self.required_modules)
        self.kwargs: __kwargs_nt_type = __kwargs_nt_type(**self.config.kwargs)
        self.root_manager = None
        self.iteration = 0
        self.__modules_nt_type = __modules_nt_type
        self.__kwargs_nt_type = __kwargs_nt_type

    def load(self, manager: "SeriesManager"):
        self.root_manager = manager
        self.modules = self.__modules_nt_type(**{
            mod_name: import_module(mod_name) for mod_name in self.required_modules
        })
        kwargs = self.load_kwargs(self.config.kwargs)
        kwargs_tpl = namedtuple(self.name, list(kwargs))
        self.kwargs = kwargs_tpl(**kwargs)
        self.properties = self.load_properties(self.config.properties)
        self.items = self.load_items(self.config.items)
        self.validate()

        if self.config.expression and isinstance(self.config.expression, str):
            self.expression = manager.load_expression(self.config.expression)

    def load_items(self, items: list[any]) -> list[any]:
        return items

    def load_properties(self, properties: dict[str, any]) -> dict[str, any]:
        return properties

    def load_kwargs(self, kwargs: dict[str, any]) -> dict[str, any]:
        return kwargs

    def validate(self):
        pass

    def compile(self):
        generated = self.generate()
        value = self.expression(
            new=self.start if self.start and not self.iteration else generated,
            interval=self.iteration,
        )
        if value is None:
            value = generated
        elif not isinstance(value, type(generated)):
            value = type(generated)(value)
        self.iteration += 1
        return value

    def generate(self):
        raise NotImplemented("Generator has not implemented `generate` method")


def register(property_generator: Type[PropertyGenerator]):
    assert property_generator.name, "Property Generator must have a name specified"
    assert property_generator.name not in GENERATORS, (f"Property Generator "
                                                       f"'{property_generator.name}' "
                                                       f"already registered")
    GENERATORS[property_generator.name] = property_generator
    return property_generator


def get_generator(config: model.PropertyDefinition, manager) -> PropertyGenerator:
    prop_gen_cls = GENERATORS[config.type]
    new_config = model.PropertyDefinition(name=config.name, type=config.type, **prop_gen_cls.default_config)
    new_config.update__(config)
    new_gen = prop_gen_cls(new_config)
    new_gen.load(manager)
    return new_gen


def _load_generator_dir(module_name: str, directory: Path):
    for _file in directory.iterdir():
        if not _file.suffix.startswith(".py") or _file.is_dir() or _file.name.startswith("_"):
            continue
        basename = _file.name.split(".")[0]
        mod = import_module(f"{module_name}.{basename}")


def load_generators():
    _load_generator_dir("syntrend.generators", Path(__file__).parent)
    add_generator_pkg = Path(CONFIG.config.generator_dir).absolute()
    if not (add_generator_pkg.is_dir() and add_generator_pkg.exists()):
        return
    import sys
    generator_pkg_name = add_generator_pkg.name
    sys.path.append(str(add_generator_pkg))
    _load_generator_dir(generator_pkg_name, add_generator_pkg)
