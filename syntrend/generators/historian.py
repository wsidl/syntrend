from syntrend.config import CONFIG
from typing import Union, Annotated
from annotated_types import Le

T_NegInt = Annotated[int, Le(0)]


class Historian(list):
    def __init__(self):
        super().__init__()
        self.clear()

    # Historian Manager methods
    def __get_value(self, item: T_NegInt = 0):
        offset = item - 1
        list_size = super().__len__()
        if list_size == 0:
            raise ValueError("No values added to historian")
        if -offset <= list_size:
            return super().__getitem__(offset)
        return super().__getitem__(0)

    def __getitem__(self, item: T_NegInt) -> Union[str, int, float]:
        return self.__get_value(item)

    def __call__(self, item: T_NegInt = 0):
        return self.__get_value(item)

    def append(self, _object):
        super().append(_object)
        while super().__len__() > CONFIG.config.max_historian_buffer:
            super().pop(0)

    def has_values(self) -> bool:
        return super().__len__() > 0

    ##########################################################
    # Convenience Operators when defaulting to current value #
    ##########################################################
    @property
    def current(self):
        return super().__getitem__(-1)

    # Comparator Methods
    def __eq__(self, other):
        return self.current == other

    def __ne__(self, other):
        return self.current != other

    def __lt__(self, other):
        return self.current < other

    def __le__(self, other):
        return self.current <= other

    def __gt__(self, other):
        return self.current > other

    def __ge__(self, other):
        return self.current >= other

    # Arithmetic Operators
    def __add__(self, other):
        return self.current + other

    def __sub__(self, other):
        return self.current - other

    def __mul__(self, other):
        return self.current * other

    # Formatting / Type Casting
    def __len__(self):
        return super().__len__()

    def __int__(self):
        return int(self.current)

    def __float__(self):
        return float(self.current)

    def __hex__(self):
        current = self.current
        if isinstance(current, int):
            return hex(current)
        if isinstance(current, float):
            return current.hex()
        raise TypeError("Value in this series cannot be converted to Hexadecimal")

    def __format__(self, format_spec):
        return format(self.current, format_spec)

    def __str__(self):
        return str(self.current)

    def __repr__(self):
        return str(self.current)

    # Removing unwanted methods
    def insert(self, _, __):
        raise AttributeError("'Historian' object has no attribute 'insert'")

    def __iter__(self):
        raise AttributeError("'Historian' object has no attribute '__iter__'")

    def __next__(self):
        raise AttributeError("'Historian' object has no attribute '__next__'")

    def __contains__(self, item):
        raise AttributeError("'Historian' object has no attribute '__contains__'")

