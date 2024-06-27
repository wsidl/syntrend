from event_gen.utils import parse

from pytest import mark


@mark.parametrize("version", ["2020-12"])
def test_loading_simple_json_schema_file(version):
    content = parse.parse_content_format(f"tests/assets/simple_object_{version}.schema.json")
    assert isinstance(content, dict)
    expected_keys = {"$schema", "$id", "type"}
    assert set(content.keys()).intersection(expected_keys) == expected_keys, "Keys are not matching"
    assert version in content["$schema"], "Version should be in the schema URI"


@mark.parametrize("version", ["2020-12"])
def test_loading_simple_yaml_schema_file(version):
    content = parse.parse_content_format(f"tests/assets/simple_object_{version}.schema.json")
    assert isinstance(content, dict)
    expected_keys = {"$schema", "$id", "type"}
    assert set(content.keys()).intersection(expected_keys) == expected_keys, "Keys are not matching"
    assert version in content["$schema"], "Version should be in the schema URI"
