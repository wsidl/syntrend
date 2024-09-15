from typing import Type, Callable, Union


class BaseType:
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    def __str__(self):
        return str(self.render())

    def render(self):
        raise NotImplementedError("Generator Class has not updated it's `render` method")

    def __hash__(self):
        return hash(self.render())

    def __eq__(self, other):
        return self.render() == other

    def __ne__(self, other):
        return self.render() != other


class CollectionType(BaseType):
    def __getitem__(self, item):
        return self.render()[item]

    def __len__(self):
        return len(self.render())

    def __contains__(self, item):
        return item in self.render()


class BooleanType(BaseType):
    def __and__(self, other):
        return self.render() & other

    def __or__(self, other):
        return self.render() | other

    def __xor__(self, other):
        return self.render() ^ other

    def __rxor__(self, other):
        return other ^ self.render()

    def __invert__(self):
        return ~self.render()

    def __bool__(self):
        return bool(self.render())


class NumericType(BaseType):
    def __int__(self):
        return int(self.render())

    def __float__(self):
        return float(self.render())

    def __add__(self, other):
        return self.render() + other

    def __radd__(self, other):
        return other + self.render()

    def __sub__(self, other):
        return self.render() - other

    def __rsub__(self, other):
        return other - self.render()

    def __mul__(self, other):
        return self.render() * other

    def __rmul__(self, other):
        return other * self.render()

    def __truediv__(self, other):
        return self.render() / other

    def __rtruediv__(self, other):
        return other / self.render()

    def __floordiv__(self, other):
        return self.render() // other

    def __rfloordiv__(self, other):
        return other // self.render()

    def __mod__(self, other):
        return self.render() % other

    def __rmod__(self, other):
        return other % self.render()

    def __pow__(self, other):
        return self.render() ** other

    def __rpow__(self, other):
        return other ** self.render()

    def __lt__(self, other):
        return self.render() < other

    def __le__(self, other):
        return self.render() <= other

    def __gt__(self, other):
        return self.render() > other

    def __ge__(self, other):
        return self.render() >= other

    def __abs__(self):
        return abs(self.render())


class StringType(CollectionType):
    pass


class IntegerType(NumericType):
    def __rshift__(self, other):
        return self.render() >> other

    def __lshift__(self, other):
        return self.render() << other


class FloatType(NumericType):
    def __round__(self, n=None):
        return round(self.render(), n)


class ListType(CollectionType):
    pass


class MappingType(CollectionType):
    def __getattr__(self, name):
        return self.properties[name]


EXPRESSION_TYPES = {
    str: StringType,
    int: IntegerType,
    float: FloatType,
    bool: BooleanType,
    list: ListType,
    dict: MappingType,
}
AVAILABLE_TYPES = set(EXPRESSION_TYPES.values())
T_TYPE_MAP = dict[str, set[Union[str, Type[BaseType]]]]


def __load_type_methods(type_map: T_TYPE_MAP, root_type_name: str, type_object):
    type_name = type_object.__name__
    for prop in type_object.__dict__:
        if not isinstance(getattr(type_object, prop), Callable):
            continue
        if prop not in type_map:
            type_map[prop] = set()
        type_map[prop].add(root_type_name)
    type_map['LOADED'].add(type_name)
    for base_type in type_object.__mro__[1:]:
        base_name = base_type.__name__
        if base_name == type_name:
            continue
        if not base_name.endswith('Type') or base_name == 'BaseType':
            continue
        __load_type_methods(type_map, root_type_name, base_type)


def load_type_method_mapping() -> dict[str, set[Type[BaseType]]]:
    type_methods = {'LOADED': set()}
    for _type in EXPRESSION_TYPES:
        __load_type_methods(
            type_methods, EXPRESSION_TYPES[_type].__name__, EXPRESSION_TYPES[_type]
        )
    type_methods.pop('LOADED')
    return type_methods


class AnyTime:
    def __init__(self, generator):
        self.generator = generator

    def __getattribute__(self, item):
        pass


TYPE_MAPPING = load_type_method_mapping()


def load_type(generator):
    if generator.type is None:
        return generator
    base_type = EXPRESSION_TYPES[generator.type]
    if base_type in generator.__bases__:
        return generator
    return type(
        generator.__name__,
        tuple(list(generator.__bases__) + [base_type]),
        generator.__dict__ | base_type.__dict__,
    )
