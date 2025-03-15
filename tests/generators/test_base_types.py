from syntrend.generators import RenderValue
from syntrend.generators import __base_types as base

from pytest import mark


class BaseTestType:
    def __init__(self, value):
        self.value = value

    def render(self):
        return RenderValue(self.value, self.value)


class IntegerType(BaseTestType):
    type = int


@mark.unit
def test_base_type_comparators():
    new_type = base.load_type(IntegerType)
    t = new_type(5)
    assert str(t) == '5', (
        'Generator should represent itself as a string parse of the current value'
    )
    assert hash(t) == 5, 'Hash of generator should be the hash of the current value'
    assert t == 5, 'Equality should be the equality of its current value'
    assert t != 6, 'Non-Equality should be based on the current value'


@mark.unit
def test_number_type_operands():
    new_type = base.load_type(IntegerType)
    generator = new_type('5')
    assert int(generator) == 5, (
        'Integer translation of the generator should use the current value'
    )
    assert float(generator) == 5.0, (
        'Float translation of the generator should use the current value'
    )
    assert generator + 1 == 6, 'Addition of the generator should use the current value'
    assert 1 + generator == 6, (
        'Reverse addition of the generator should use the current value'
    )
    assert generator - 1 == 4, (
        'Subtraction of the generator should use the current value'
    )
    assert 1 - generator == -4, (
        'Reverse subtraction of the generator should use the current value'
    )
    assert generator * 2 == 10, (
        'Multiplication of the generator should use the current value'
    )
    assert 2 * generator == 10, (
        'Reverse Multiplication of the generator should use the current value'
    )
    assert generator / 2 == 2.5, (
        'Division of the generator should use the current value'
    )
    assert 180 / generator == 36, (
        'Reverse Division of the generator should use the current value'
    )
    assert generator // 2 == 2, (
        'Floor Division of the generator should use the current value'
    )
    assert 78 // generator == 15, (
        'Reverse Floor Division of the generator should use the current value'
    )
    assert generator % 3 == 2, 'Modulo of the generator should use the current value'
    assert 78 % generator == 3, (
        'Reverse Modulo of the generator should use the current value'
    )
    assert generator**2 == 25, 'Power of the generator should use the current value'
    assert 2**generator == 32, 'Generator used as a power should use the current value'


@mark.unit
def test_number_type_comparators():
    new_type = base.load_type(IntegerType)
    generator = new_type('5')
    assert generator < 6, (
        'Generator should compare as less than other numbers using the current value'
    )
    assert generator <= 5 and generator <= 7, (
        'Generator should compare as less than or equal to other numbers using the current value'
    )
    assert generator > 4, (
        'Generator should compare as greater than other numbers using the current value'
    )
    assert generator >= 4 and generator >= 5, (
        'Generator should compare as greater than or equal to other numbers using the current value'
    )
    negative_generator = new_type('-5')
    assert abs(generator) == 5 and abs(negative_generator) == 5, (
        'Absolute of the generator should use the current value'
    )


@mark.unit
def test_integer_type_operators():
    new_type = base.load_type(IntegerType)
    generator = new_type('500')
    assert generator >> 2 == 125, (
        'Right Shift of the Generator should use the current value'
    )
    assert generator << 2 == 2000, (
        'Left Shift of the Generator should use the current value'
    )


class FloatType(BaseTestType):
    type = float


@mark.unit
def test_integer_type_operators():
    new_type = base.load_type(FloatType)
    generator = new_type('2.878')
    assert round(generator, 1) == 2.9, (
        'Rounding of Float Generator should return the current value rounded'
    )


class BoolType(BaseTestType):
    type = bool


@mark.unit
def test_boolean_type_operators():
    new_type = base.load_type(BoolType)
    true_generator = new_type(1)
    false_generator = new_type(0)
    assert true_generator == True and false_generator == False, (
        'Generator should use the current value for equality'
    )
    assert not false_generator, 'Generator should represent itself as a boolean'
    assert true_generator, 'Generator should represent itself as a boolean'
    assert true_generator & True, 'Generator should be perform an AND operation'
    assert false_generator | True, 'Generator should be perform an OR operation'
    assert true_generator ^ False, 'Generator should be perform an XOR operation'
    assert True ^ false_generator, (
        'Generator should be perform an XOR operation as a reverse'
    )
    assert bool(true_generator), 'Generator should translate to a boolean value'


class ListType(BaseTestType):
    type = list


@mark.unit
def test_list_type_operators():
    new_type = base.load_type(ListType)
    generator = new_type([1, 2, 3])
    assert generator[2] == 3, (
        'Index Retrieval of the generator should return the item in the current list'
    )
    assert len(generator) == 3, (
        'Length of generator should be the length of its current value'
    )
    assert 1 in generator, (
        'Containment check of the generator should be against its current value'
    )


class DictType(BaseTestType):
    type = dict


@mark.unit
def test_dict_type_operator():
    new_type = base.load_type(DictType)
    generator = new_type({'a': 2, 'b': 'test'})
    generator.properties = generator.value
    assert generator['a'] == 2, (
        'Key Retrieval of the generator should return the item in the current list'
    )
    assert len(generator) == 2, (
        'Length of generator should be the length of its current value'
    )
    assert 'b' in generator, (
        'Containment check of the generator should be against its current value'
    )
    assert generator.b == 'test', (
        'Attribute retrieval of the generator should return an item in its dictionary'
    )
