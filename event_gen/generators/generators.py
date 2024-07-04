from event_gen.config import model

from random import randint, random
from typing import Callable, Union, TypeVar
from copy import deepcopy
import string

from faker import Faker
from jinja2 import Environment

T = TypeVar('T')
T_State = dict[str, any]
T_CB_Gen = Callable[[T], T]
T_CB_BaseGen = Callable[["ObjectGenerator", model.PropertyDefinition], T_CB_Gen]

fake = Faker()
GENERATORS: dict[str, tuple[T_State, T_CB_BaseGen]] = {}


def register_generator(name: str, default_config: T_State):

    def __load_generator(func_gen: T_CB_BaseGen):
        if name in GENERATORS:
            raise KeyError(f"Generator with name '{name}' already exists")
        GENERATORS[name] = (default_config, func_gen)

        return func_gen

    return __load_generator


def load_generator(name: str, root_obj, config: model.PropertyDefinition) -> T_CB_Gen:
    default_config, func_gen = GENERATORS[name]
    new_config = model.PropertyDefinition(name_=config.name_, type=name, **default_config)
    new_config.update__(config)

    return func_gen(root_obj, new_config)


@register_generator("static", {"expression": None})
def static_generator(root_obj, cfg: model.PropertyDefinition):
    assert cfg.expression is not None, "Static Generator requires a value to be provided"

    def _gen(seed: any = None):
        if seed is not None:
            return seed
        return cfg.expression

    return _gen


@register_generator("items", {"items": []})
def item_generator(root_obj, cfg: model.PropertyDefinition):
    items = cfg.prop_config["items"]
    item_count = len(items) - 1
    assert item_count >= 0, "Cannot generate items from an empty list"

    def __generator(seed: list[any] = None):
        if seed is not None and len(seed) > 0:
            return seed
        return items[randint(0, item_count)]

    return __generator


@register_generator("string", {
    "chars": string.ascii_letters + string.digits,
    "min_length": 6,
    "max_length": 20,
})
def string_generator(root_obj, cfg: model.PropertyDefinition):
    assert len(cfg.prop_config["chars"]) > 0, "Cannot generate random strings without a list of chars"
    assert (
        int(cfg.prop_config["min_length"]) <= int(cfg.prop_config["max_length"]),
        "Min Char length must be less than the Max Char length",
    )
    chars_length = len(cfg.prop_config["chars"]) - 1
    min_len = int(cfg.prop_config["min_length"])
    max_len = int(cfg.prop_config["max_length"])
    unique_chars = set(cfg.prop_config["chars"])
    expr = cfg.expression

    def _generator(seed: str = None):
        if seed is not None and min_len <= len(seed) <= max_len and set(seed).issubset(unique_chars) and isinstance(seed, str):
            return seed
        return "".join([
            cfg.prop_config["chars"][randint(0, chars_length)]
            for _ in range(randint(min_len, max_len))
        ])

    return _generator


@register_generator("integer", {
    "min_integer": -500,
    "max_integer": 500,
})
def integer_generator(root_obj, cfg: model.PropertyDefinition):
    min_int = int(cfg.prop_config["min_integer"])
    max_int = int(cfg.prop_config["max_integer"])

    def _generator(seed: int = None):
        if seed is not None and min_int <= seed <= max_int and isinstance(seed, int):
            return seed
        return randint(min_int, max_int)

    return _generator


@register_generator("float", {
    "min_float": -500.0,
    "max_float": 500.0,
    "num_decimals": 6,
})
def float_generator(root_obj, cfg: model.PropertyDefinition):
    min_flt = float(cfg.prop_config["min_float"])
    max_flt = float(cfg.prop_config["max_float"])
    num_decimals = int(cfg.prop_config["num_decimals"])
    float_range = max_flt - min_flt

    def _generator(seed: float = None) -> float:
        if seed is not None and min_flt <= seed <= max_flt and isinstance(seed, float):
            return round(seed, num_decimals)
        return round(random() * float_range + min_flt, num_decimals)

    return _generator


@register_generator("hex", {
    "use_upper": False,
    "max_length": 20,
    "min_length": 6,
    "chars": "0123456789abcdef",
})
def hex_generator(root_obj, cfg: model.PropertyDefinition):
    min_len = int(cfg.prop_config["min_length"])
    max_len = int(cfg.prop_config["max_length"])
    chars_length = len(cfg.prop_config["chars"])
    chars = cfg.prop_config["chars"]
    if cfg.prop_config["use_upper"]:
        chars = chars.upper()

    def _generator(seed: Union[str, hex] = None):
        if seed is not None and min_len <= len(str(seed)) <= max_len and isinstance(seed, Union[str, hex]):
            return str(hex(seed))
        return "".join([chars[randint(0, chars_length - 1)] for _ in range(randint(min_len, max_len))])

    return _generator


@register_generator("uuid", {
    "use_upper": False,
    "compact": False,
})
def uuid_generator(root_obj, cfg: model.PropertyDefinition):
    from uuid import uuid4, UUID

    def _generator(seed: str = None):
        if seed is not None and len(seed) > 0:
            uuid_val = UUID(seed)
        else:
            uuid_val = uuid4()
        if cfg.prop_config["compact"]:
            uuid_val = uuid_val.hex
        else:
            uuid_val = str(uuid_val)
        if cfg.prop_config["use_upper"]:
            uuid_val = uuid_val.upper()
        return uuid_val

    return _generator


@register_generator("name", {})
def name_generator(root_obj, cfg: model.PropertyDefinition):
    def _generator(seed: str = None):
        if seed is not None and len(seed) > 0:
            return seed
        return fake.name()

    return _generator


@register_generator("first_name", {})
def first_name_generator(root_obj, cfg: model.PropertyDefinition):
    def _generator(seed: str = None):
        if seed is not None and len(seed) > 0:
            return seed
        return fake.first_name()

    return _generator


@register_generator("last_name", {})
def last_name_generator(root_obj, cfg: model.PropertyDefinition):
    def _generator(seed: str = None):
        if seed is not None and len(seed) > 0:
            return seed
        return fake.last_name()

    return _generator


@register_generator("object", {"properties": {}})
def object_generator(root_obj: "model.ObjectDefinition", cfg: model.PropertyDefinition):
    property_gens = {
        key: load_generator(prop.type, root_obj, prop)
        for key, prop in cfg.properties.items()
    }

    def _generator(seed: dict[str, any] = None):
        if seed is not None and len(seed) > 0 and seed.keys() == property_gens.keys():
            return seed
        return {
            _key: property_gens[_key]()
            for _key in property_gens
        }

    return _generator
