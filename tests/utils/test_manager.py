from syntrend.utils import manager

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
    with raises(ValueError) as exc:
        manager.prepare_dependency_tree(dependencies)
    assert exc.type == ValueError
    assert exc.value.args[0].startswith("Circular dependency with ")
    expected = [sorted(a) for a in expected]
    for group in exc.value.args[1]:
        assert sorted(group) in expected


