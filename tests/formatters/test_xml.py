from syntrend.formatters import xml, Event, Collection

from pytest import mark, fixture, raises


@fixture(scope='function')
def xml_formatter(patch_formatter):
    def _setup(config: dict):
        patch_formatter(xml, config)
        return xml.xml_formatter('test')

    return _setup


@mark.issue(id=15)
@mark.unit
def test_minimum_xml(xml_formatter):
    formatter = xml_formatter(
        {'type': 'object', 'properties': {'value': {'type': 'string'}}}
    )
    output = formatter(Collection(Event({'value': 'generated_string'})))
    assert len(output) == 2, 'Generated XML should contain 4 lines'
    assert output[0] == '<?xml version="1.0" encoding="utf-8"?>', (
        'Output String should contain the namespace xml header'
    )
    assert output[1] == '<test>generated_string</test>', (
        'Output XML should have the provided string enclosed by tags of the generated object'
    )


@mark.issue(id=15)
@mark.unit
def test_two_values(xml_formatter):
    formatter = xml_formatter(
        {
            'type': 'object',
            'properties': {'attr': {'type': 'string'}, 'value': {'type': 'string'}},
        }
    )
    output = formatter(
        Collection(Event({'attr': 'attribute', 'value': 'value_string'}))
    )
    assert len(output) == 5, 'Generated XML should contain 2 lines'
    assert output[1:] == ['<test>', '  attribute', '  value_string', '</test>'], (
        'Generated XML should have both properties concatenated'
    )


@mark.issue(id=15)
@mark.unit
def test_value_as_attribute(xml_formatter):
    formatter = xml_formatter(
        {
            'type': 'object',
            'properties': {
                'attr': {'type': 'string', 'xml_attr': True},
                'value': {'type': 'string'},
            },
        }
    )
    output = formatter(
        Collection(Event({'attr': 'attribute', 'value': 'value_string'}))
    )
    assert len(output) == 2, 'Generated XML should contain 2 lines'
    assert output[1] == '<test attr="attribute">value_string</test>', (
        'Generated XML should have `attr` as the XML Attribute and Value nested within'
    )


@mark.issue(id=15)
@mark.unit
def test_mixed_type_nested_objects(xml_formatter):
    formatter = xml_formatter(
        {
            'type': 'object',
            'properties': {
                'attr': {'type': 'string', 'xml_attr': True},
                'child1': {'type': 'string'},
                'child2': {
                    'type': 'object',
                    'properties': {'content': {'type': 'string'}},
                },
                'child3': {'type': 'integer'},
            },
        }
    )
    output = formatter(
        Collection(
            Event(
                {
                    'attr': 'attribute',
                    'child1': 'first_element',
                    'child2': {'content': 'string2'},
                    'child3': 9000,
                }
            )
        )
    )
    assert len(output) == 6, 'Generated XML should contain 4 lines'
    assert output[1] == '<test attr="attribute">', (
        'Nested Objects span multiple lines, should have the opening xml tag'
    )
    assert output[2] == '  first_element', 'First string is the first test element'
    assert output[3] == '  <child2>string2</child2>', 'Followed by nested element'
    assert output[4] == '  9000', 'Ends with number added after'
    assert output[5] == '</test>', 'Closing tag should be last'


@mark.issue(id=15)
@mark.unit
def test_hybrid_nested_types(xml_formatter):
    formatter = xml_formatter(
        {
            'type': 'object',
            'properties': {
                'attr': {'type': 'string', 'xml_attr': True},
                'child1': {
                    'type': 'object',
                    'properties': {'content': {'type': 'string'}},
                },
                'child2': {
                    'type': 'object',
                    'properties': {'content': {'type': 'string'}},
                },
            },
        }
    )
    output = formatter(
        Collection(
            Event(
                {
                    'attr': 'attribute',
                    'child1': {'content': 'string1'},
                    'child2': {'content': 'string2'},
                }
            )
        )
    )
    assert len(output) == 5, 'Generated XML should contain 5 lines'
    assert output[1] == '<test attr="attribute">', (
        'Nested Objects span multiple lines, should have the opening xml tag'
    )
    assert output[2] == '  <child1>string1</child1>', (
        'First nested object should only contain a string'
    )
    assert output[3] == '  <child2>string2</child2>', (
        'Second nested object should only contain a string'
    )
    assert output[4] == '</test>', 'Closing tag should be last'


@mark.issue(id=15)
@mark.unit
def test_nested_objects(xml_formatter):
    formatter = xml_formatter(
        {
            'type': 'object',
            'properties': {
                'attr': {'type': 'string', 'xml_attr': True},
                'child1': {
                    'type': 'object',
                    'xml_tag': 'child',
                    'properties': {'content': {'type': 'string'}},
                },
                'child2': {
                    'type': 'object',
                    'xml_tag': 'child',
                    'properties': {'content': {'type': 'string'}},
                },
            },
        }
    )
    output = formatter(
        Collection(
            Event(
                {
                    'attr': 'attribute',
                    'child1': {'content': 'string1'},
                    'child2': {'content': 'string2'},
                }
            )
        )
    )
    assert len(output) == 5, 'Generated XML should contain 5 lines'
    assert output[1] == '<test attr="attribute">', (
        'Nested Objects span multiple lines, should have the opening xml tag'
    )
    assert output[2] == '  <child>string1</child>', (
        'First nested object should only contain a string and use the provided `xml_tag`'
    )
    assert output[3] == '  <child>string2</child>', (
        'Second nested object should only contain a string and use the provided `xml_tag`'
    )
    assert output[4] == '</test>', 'Closing tag should be last'


@mark.issue(id=15)
@mark.unit
def test_nested_list_of_objects(xml_formatter):
    formatter = xml_formatter(
        {
            'type': 'object',
            'properties': {
                'attr': {'type': 'string', 'xml_attr': True},
                'children': {
                    'type': 'list',
                    'sub_type': {
                        'type': 'object',
                        'xml_tag': 'child',
                        'properties': {'content': {'type': 'string'}},
                    },
                },
            },
        }
    )
    output = formatter(
        Collection(
            Event(
                {
                    'attr': 'attribute',
                    'children': [{'content': 'string1'}, {'content': 'string2'}],
                }
            )
        )
    )
    assert len(output) == 5, 'Generated XML should contain 5 lines'
    assert output[1] == '<test attr="attribute">', (
        'Nested Objects span multiple lines, should have the opening xml tag'
    )
    assert output[2] == '  <child>string1</child>', (
        'First nested object should only contain a string and use the provided `xml_tag`'
    )
    assert output[3] == '  <child>string2</child>', (
        'Second nested object should only contain a string and use the provided `xml_tag`'
    )
    assert output[4] == '</test>', 'Closing tag should be last'


@mark.issue(id=15)
@mark.unit
def test_collection_nested_list_of_object(xml_formatter):
    formatter = xml_formatter(
        {
            'output': {'collection': True, 'xml_tag': 'root'},
            'type': 'object',
            'properties': {
                'attr': {'type': 'string', 'xml_attr': True},
                'children': {
                    'type': 'list',
                    'sub_type': {
                        'type': 'object',
                        'xml_tag': 'child',
                        'properties': {'content': {'type': 'string'}},
                    },
                },
            },
        }
    )
    output = formatter(
        Collection(
            Event(
                {
                    'attr': 'attribute1',
                    'children': [{'content': 'string1'}, {'content': 'string2'}],
                }
            ),
            Event(
                {
                    'attr': 'attribute2',
                    'children': [{'content': 'string3'}, {'content': 'string4'}],
                }
            ),
        )
    )
    assert len(output) == 11, 'Generated XML should contain 11 lines'
    assert output[1] == '<root>' and output[10] == '</root>', (
        'Root element is the enclosing collection tag'
    )
    assert (
        output[2] == '  <test attr="attribute1">'
        and output[6] == '  <test attr="attribute2">'
    ), 'There should be two instances of the root object'
    assert output[5] == output[9] and output[5] == '  </test>', (
        'Each enclosed object should be closed'
    )
    assert output[3:5] == [
        '    <child>string1</child>',
        '    <child>string2</child>',
    ], 'First object should contain two children'
    assert output[7:9] == [
        '    <child>string3</child>',
        '    <child>string4</child>',
    ], 'Second object should contain two children'


@mark.unit
def test_invalid_attribute_type_definition(xml_formatter):
    formatter = xml_formatter(
        {
            'type': 'object',
            'properties': {
                'attr': {
                    'type': 'list',
                    'xml_attr': True,
                    'sub_type': {'type': 'string'},
                },
            },
        }
    )
    with raises(TypeError) as result:
        formatter(Collection(Event({'attr': 'test_string'})))
        assert result.type is TypeError, (
            'Formatting of an attribute list type should raise TypeError'
        )


@mark.unit
def test_invalid_attribute_value_type(xml_formatter):
    formatter = xml_formatter(
        {'type': 'object', 'properties': {'attr': {'type': 'string', 'xml_attr': True}}}
    )
    with raises(ValueError) as result:
        formatter(Collection(Event({'attr': ['test_string']})))
        assert result.type is ValueError, (
            'Formatting of an attribute list value should raise ValueError'
        )
    with raises(ValueError) as result:
        formatter(Collection(Event({'attr': {'a': 'test_string'}})))
        assert result.type is ValueError, (
            'Formatting of an attribute dict value should raise ValueError'
        )


@mark.issue(id=25)
@mark.unit
def test_multiple_documents(xml_formatter):
    formatter = xml_formatter(
        {
            'type': 'object',
            'properties': {
                'attr': {'type': 'string', 'xml_attr': True},
                'value': {'type': 'string'},
            },
        }
    )
    output1 = formatter(
        Collection(Event({'attr': 'attribute1', 'value': 'first_string'}))
    )
    assert output1[1] == '<test attr="attribute1">first_string</test>', (
        'Generated XML should have `attr` as the XML Attribute and Value nested within'
    )
    output2 = formatter(
        Collection(Event({'attr': 'attribute2', 'value': 'second_string'}))
    )
    assert output2[1] == '<test attr="attribute2">second_string</test>', (
        'Generated XML should have `attr` as the XML Attribute and Value nested within'
    )
