import syntrend.config.model.property_definition as mod
from pytest import mark, raises


@mark.issue(id=30)
@mark.unit
def test_init_no_type_raises_error():
    with raises(ValueError) as exc:
        _ = mod.PropertyDefinition(
            name='no_type',
            type=mod.NullValue(),
        )
    assert exc.type is ValueError, 'Should raise ValueError'
    assert exc.value.args[0] == 'No type provided', 'Should say `type` was not provided'
    assert exc.value.args[1]['Object'] == 'no_type', (
        'Should share the name of the object'
    )
