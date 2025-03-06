from syntrend.formatters import ascii_table, Event, Collection

from pytest import mark


@mark.unit
def test_single_string(patch_formatter):
    patch_formatter(ascii_table, {'type': 'string'})
    formatter = ascii_table.table_formatter('test')
    output = formatter(Collection(Event('generated_string')))
    assert output[0] == ' generated_string ', 'Should generate a quoted string'


@mark.unit
def test_single_number(patch_formatter):
    patch_formatter(ascii_table, {'type': 'integer'})
    formatter = ascii_table.table_formatter('test')
    output = formatter(Collection(Event(10)))
    assert output[0] == '    10 ', 'Should generate an encoded number string'


@mark.unit
def test_single_object(patch_formatter):
    patch_formatter(ascii_table, {'type': 'object'})
    formatter = ascii_table.table_formatter('test')
    output = formatter(Collection(Event({'f1': 'string', 'f2': 10})))
    assert output[0] == ' string 10 ', (
        'Should generate an encoded ascii_table string of multiple values'
    )


@mark.unit
def test_single_object_w_col_sep(patch_formatter):
    patch_formatter(
        ascii_table, {'type': 'object', 'output': {'column_separator': '|'}}
    )
    formatter = ascii_table.table_formatter('test')
    output = formatter(Collection(Event({'f1': 'string', 'f2': 10})))
    assert output[0] == ' string | 10 ', (
        'Should generate an encoded ascii_table string of multiple values'
    )


@mark.unit
def test_multiple_objects(patch_formatter):
    patch_formatter(ascii_table, {'type': 'object'})
    formatter = ascii_table.table_formatter('test')
    output = formatter(
        Collection(
            Event({'f1': 'string', 'f2': 10}),
            Event({'f1': 'string', 'f2': 10}),
            Event({'f1': 'string', 'f2': 10}),
        )
    )
    assert output[0] == ' string 10 ', (
        'Should generate an encoded ascii_table string of multiple values'
    )
    assert len(output) == 3, (
        'Should generate 3 lines of ascii_table output with an extra empty line'
    )


@mark.unit
def test_multiple_objects_as_collection(patch_formatter):
    patch_formatter(ascii_table, {'type': 'object', 'output': {'collection': True}})
    formatter = ascii_table.table_formatter('test')
    output = formatter(
        Collection(
            Event({'f1': 'string', 'f2': 10}),
            Event({'f1': 'string', 'f2': 10}),
            Event({'f1': 'string', 'f2': 10}),
        )
    )
    assert output[0] == ' f1     f2 ', 'First line should include a list encapsulation'
    assert output[1] == '===========', 'Second line should be the header separator'
    assert output[2] == ' string 10 ', (
        'Should generate an indented ascii_table string of multiple values'
    )
    assert len(output) == 5, (
        'Should generate 3 lines of an asciitable, header and header separator'
    )


@mark.unit
def test_multiple_objects_as_collection_w_col_sep(patch_formatter):
    patch_formatter(
        ascii_table,
        {'type': 'object', 'output': {'collection': True, 'column_separator': '|'}},
    )
    formatter = ascii_table.table_formatter('test')
    output = formatter(
        Collection(
            Event({'f1': 'string', 'f2': 10}),
            Event({'f1': 'string', 'f2': 10}),
            Event({'f1': 'string', 'f2': 10}),
        )
    )
    assert output[0] == ' f1     | f2 ', (
        'First line should include a list encapsulation'
    )
    assert output[1] == '=============', 'Second line should be the header separator'
    assert output[2] == ' string | 10 ', (
        'Should generate an indented ascii_table string of multiple values'
    )
    assert len(output) == 5, (
        'Should generate 3 lines of an asciitable, header and header separator'
    )


@mark.unit
def test_multiple_objects_as_collection_w_row_sep(patch_formatter):
    patch_formatter(
        ascii_table,
        {'type': 'object', 'output': {'collection': True, 'row_separator': '-'}},
    )
    formatter = ascii_table.table_formatter('test')
    output = formatter(
        Collection(
            Event({'f1': 'string', 'f2': 10}),
            Event({'f1': 'string', 'f2': 10}),
            Event({'f1': 'string', 'f2': 10}),
        )
    )
    assert output[0] == ' f1     f2 ', 'First line should include a list encapsulation'
    assert output[1] == '===========', 'Second line should be the header separator'
    assert output[2] == ' string 10 ', (
        'Should generate an ascii_table string of multiple values'
    )
    assert output[3] == '-----------', 'Lines between rows should use the row separator'
    assert len(output) == 8, (
        'Should generate 3 lines of an asciitable, 2 lines with row separator, header and header separator'
    )
