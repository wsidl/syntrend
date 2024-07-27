from syntrend.utils import historian

from pytest import mark


# @mark.parametrize(
#     "test_path,groups",
#     [
#         ("self", ("", None, "")),
#         ("self.a", ("self", None, "a")),
#         ("self.a.b.c", ("self", None, "a.b.c")),
#         ("self[0]", ("self", "0", "")),
#         ("self[4].a", ("self", "4", "a")),
#         ("self[25].a.b.c", ("self", "25", "a.b.c")),
#         ("self[-1][4]", ("self", "-1", "[4]")),
#         ("self[4][-1].a", ("self", "4", "[-1].a")),
#         ("self[25][?b=='c'].a.b.c", ("self", "25", "[?b=='c'].a.b.c")),
#     ],
#     ids=[
#         "only root",
#         "with prop",
#         "with multiple levels",
#         "only indexed root",
#         "indexed root with property",
#         "indexed root with multiple levels",
#         "sub-item in list root",
#         "sub-item's property in list root",
#         "sub-item's property by filter in list root",
#     ]
# )
# def test_parsing_regex(test_path, groups):
#     parsed = historian.RE_PATH_ROOT.fullmatch(test_path).groups()
#     assert parsed == groups
