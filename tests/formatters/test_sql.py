from syntrend.formatters import sql, Event, Collection

from pytest import mark


@mark.unit
def test_single_string(patch_formatter):
    patch_formatter(sql, {'type': 'string'})
    formatter = sql.sql_formatter('test')
    output = formatter(Collection(Event('generated_string')))
    assert output[0] == 'insert into test (value) values ("generated_string");', (
        'Should generate an insert statement'
    )


@mark.unit
def test_single_number(patch_formatter):
    patch_formatter(sql, {'type': 'integer'})
    formatter = sql.sql_formatter('test')
    output = formatter(Collection(Event(10)))
    assert output[0] == 'insert into test (value) values (10);', (
        'Should generate an insert statement'
    )


@mark.unit
def test_single_object(patch_formatter):
    patch_formatter(sql, {'type': 'object'})
    formatter = sql.sql_formatter('test')
    output = formatter(Collection(Event({'f1': 'string', 'f2': 10})))
    assert output[0] == 'insert into test (f1, f2) values ("string", 10);', (
        'Should generate an insert statement with 2 fields'
    )


@mark.unit
def test_multiple_objects(patch_formatter):
    patch_formatter(sql, {'type': 'object'})
    formatter = sql.sql_formatter('test')
    output = formatter(
        Collection(
            Event({'f1': 'string', 'f2': 10}),
            Event({'f1': 'string', 'f2': 10}),
            Event({'f1': 'string', 'f2': 10}),
        )
    )
    assert all(
        [line == 'insert into test (f1, f2) values ("string", 10);' for line in output]
    ), 'All lines should generate an insert statement'
    assert len(output) == 3, 'Should generate 3 lines of sql output'


@mark.unit
def test_multiple_objects_as_collection(patch_formatter):
    patch_formatter(sql, {'type': 'object', 'output': {'collection': True}})
    formatter = sql.sql_formatter('test')
    output = formatter(
        Collection(
            Event({'f1': 'string', 'f2': 10}),
            Event({'f1': 'string', 'f2': 10}),
            Event({'f1': 'string', 'f2': 10}),
        )
    )
    assert all(
        [line == 'insert into test (f1, f2) values ("string", 10);' for line in output]
    ), 'All lines should generate an insert statement'
    assert len(output) == 3, (
        'Should generate 3 lines of sql output, no changes for collections'
    )
