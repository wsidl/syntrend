from event_gen.jsonschema.core import SchemaManager

from pytest import mark


@mark.parametrize("version", ["2020-12"])
def test_loading_simple_schema_file(version):
    sg = SchemaManager()
    sg.add_schema("test", f"../assets/simple_object_{version}.schema.json")
    sg.get_schema("test")


@mark.parametrize("version", ["2020-12"])
def test_loading_simple_schema_file(version):
    sg = SchemaManager()
    sg.add_schema("test", f"../assets/complex_object_{version}.schema.json")
    print(sg.get_schema("test"))
