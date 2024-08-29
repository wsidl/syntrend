from syntrend.formatters import json, Event, Collection

from pytest import mark


@mark.unit
def test_single_string(project, monkeypatch):
    project(json, {"type": "string"})
    formatter = json.json_formatter("test")
    output = formatter(Collection(Event("generated_string")))
    assert output[0] == '"generated_string"', "Should generate a quoted string"


@mark.unit
def test_single_number(project, monkeypatch):
    project(json, {"type": "integer"})
    formatter = json.json_formatter("test")
    output = formatter(Collection(Event(10)))
    assert output[0] == '10', "Should generate an encoded number string"


@mark.unit
def test_single_object(project, monkeypatch):
    project(json, {"type": "object"})
    formatter = json.json_formatter("test")
    output = formatter(Collection(Event({"f1": "string", "f2": 10})))
    assert output[0] == '{"f1": "string", "f2": 10}', "Should generate an encoded json string of multiple values"


@mark.unit
def test_multiple_objects(project, monkeypatch):
    project(json, {"type": "object"})
    formatter = json.json_formatter("test")
    output = formatter(Collection(
        Event({"f1": "string", "f2": 10}),
        Event({"f1": "string", "f2": 10}),
        Event({"f1": "string", "f2": 10})
    ))
    assert output[0] == '{"f1": "string", "f2": 10}', "Should generate an encoded json string of multiple values"
    assert len(output) == 3, "Should generate 3 lines of json output with an extra empty line"


@mark.unit
def test_multiple_objects_as_collection(project, monkeypatch):
    project(json, {"type": "object", "output": {"collection": True}})
    formatter = json.json_formatter("test")
    output = formatter(Collection(
        Event({"f1": "string", "f2": 10}),
        Event({"f1": "string", "f2": 10}),
        Event({"f1": "string", "f2": 10})
    ))
    assert output[0] == '[', "First line should include a list encapsulation"
    assert output[1] == '  {"f1": "string", "f2": 10},', "Should generate an indented json string of multiple values"
    assert (
        len(output) == 5,
        "Should generate 3 lines of json output with 2 lines for list encapsulation, and an extra empty line",
    )
