from syntrend.utils import manager
from syntrend.config import model

from pytest import mark, raises


@mark.parametrize(
    "dependencies, result", [
        ({"A": {}, "B": {}, "C": {}}, [{"A", "B", "C"}]),
        ({"A": {"B"}, "B": {}}, [{"B"}, {"A"}]),
        ({"A": {"B", "C"}, "B": {"C"}, "C": {}}, [{"C"}, {"B"}, {"A"}]),
        ({}, [])
    ],
    ids=["no_deps", "single_dep", "simple_tree", "empty_dep"]
)
def test_prepare_dependency_tree(dependencies, result):
    tree = manager.prepare_dependency_tree(dependencies)
    assert tree == result, "Dependency Tree does not match the expected result"


def test_prepare_dependency_tree_missing_dependency():
    with raises(ValueError) as exc:
        manager.prepare_dependency_tree({"A": {"B", "C"}, "B": {}})
    assert exc.type == ValueError
    assert exc.value.args[0] == "Missing leaf nodes: C"


@mark.parametrize(
    "dependencies,expected",
    [
        ({"A": {"B"}, "B": {"A"}}, [["A", "B"]]),
        ({"A": {"B"}, "B": {"C"}, "C": {"A"}}, [["A", "B", "C"]]),
        ({"A": {"B", "C"}, "B": {"C"}, "C": {"A"}}, [["A", "C"], ["A", "B", "C"]]),
        ({"A": {"D"}, "B": {"C"}, "C": {"B"}, "D": {"A"}}, [["A", "D"], ["B", "C"]]),
        ({"A": {"B", "C"}, "B": {"A"}, "C": {"A"}}, [["A", "B"], ["A", "C"]])
    ],
    ids=[
        "two_val_circular",
        "three_val_circular",
        "two_branch_circular",
        "two_set_circular",
        "two_set_common_node",
    ]
)
def test_prepare_dependency_tree_circular_dependency(dependencies, expected):
    tree = manager.prepare_dependency_tree(dependencies)
    expected = [sorted(a) for a in expected]
    for group in tree:
        assert sorted(group) in expected


@mark.parametrize(
    "property_def,result",
    [
        (model.PropertyDefinition(name="test", type="string", expression="{self}."), {"self": {"self"}}),
        (model.PropertyDefinition(name="test", type="string", expression="{other.pass}."), {"self": {"other.pass"}}),
        (model.PropertyDefinition(name="test", type="object", properties={
            "a": model.PropertyDefinition(name="a", type="string", expression="{self.b}+"),
            "b": model.PropertyDefinition(name="b", type="string"),
        }), {"self": set(), "self.a": {"self.b"}, "self.b": set()}),
    ],
    ids=[
        "reference_self",
        "reference_other_property",
        "object_property_ref_string",
    ]
)
def test_iter_property_dependencies(property_def, result):
    dependency_tree = manager.iter_property_dependencies("self", property_def)
    assert dependency_tree == result
