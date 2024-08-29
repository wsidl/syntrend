from syntrend.formatters import csv, Event, Collection

from pytest import mark


@mark.unit
def test_single_string(project, monkeypatch):
    project(csv, {"type": "string"})
    formatter = csv.csv_formatter("test")
    output = formatter(Collection(Event("generated_string")))
    assert output[0] == '"generated_string"', "Should generate a quoted string"


@mark.unit
def test_single_number(project, monkeypatch):
    project(csv, {"type": "integer"})
    formatter = csv.csv_formatter("test")
    output = formatter(Collection(Event(10)))
    assert output[0] == '10', "Should generate an encoded number string"


@mark.unit
def test_single_object(project, monkeypatch):
    project(csv, {"type": "object"})
    formatter = csv.csv_formatter("test")
    output = formatter(Collection(Event({"f1": "string", "f2": 10})))
    assert output[0] == '"string",10', "Should generate an encoded csv string of multiple values"


@mark.unit
def test_multiple_objects(project, monkeypatch):
    project(csv, {"type": "object"})
    formatter = csv.csv_formatter("test")
    output = formatter(Collection(
        Event({"f1": "string", "f2": 10}),
        Event({"f1": "string", "f2": 10}),
        Event({"f1": "string", "f2": 10})
    ))
    assert output[0] == '"string",10', "Should generate an encoded csv string of multiple values"
    assert len(output) == 4, "Should generate 3 lines of csv output with an extra empty line"


@mark.unit
def test_multiple_objects_as_collection(project, monkeypatch):
    project(csv, {"type": "object", "output": {"collection": True}})
    formatter = csv.csv_formatter("test")
    output = formatter(Collection(
        Event({"f1": "string", "f2": 10}),
        Event({"f1": "string", "f2": 10}),
        Event({"f1": "string", "f2": 10})
    ))
    assert output[0] == '"f1","f2"', "First line should include a header"
    assert output[1] == '"string",10', "Should generate an encoded csv string of multiple values"
    assert len(output) == 5, "Should generate 4 lines of csv output with header, and an extra empty line"
