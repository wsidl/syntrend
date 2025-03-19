from syntrend.config.model import base_config as mod
from pytest import mark, raises
from pathlib import Path


@mark.issue(id=7)
@mark.unit
def test_deep_update_flat_dicts_merge():
    result = mod.deep_update({'a': 1}, {'b': 2})
    assert result == {'a': 1, 'b': 2}, 'Dictionaries should be a union of the originals'


@mark.issue(id=7)
@mark.unit
def test_deep_update_flat_dict_override():
    result = mod.deep_update({'a': 1, 'c': 3}, {'a': 0, 'b': 2})
    assert result == {'a': 0, 'b': 2, 'c': 3}, (
        'Dictionaries should be a merge of the originals'
    )


@mark.issue(id=7)
@mark.unit
def test_deep_update_add_nested_dict():
    result = mod.deep_update({'a': 1, 'c': 3}, {'a': 0, 'b': {'c': 4}})
    assert result == {'a': 0, 'b': {'c': 4}, 'c': 3}, (
        'Dictionaries should be a merge of the originals'
    )


@mark.issue(id=7)
@mark.unit
def test_deep_update_update_nested_dict():
    result = mod.deep_update({'a': 1, 'b': {'c': 1}}, {'b': {'c': 4}})
    assert result == {'a': 1, 'b': {'c': 4}}, (
        'Dictionaries should be a merge of the originals'
    )


@mark.issue(id=7)
@mark.unit
def test_deep_update_update_nested_obj_type():
    result = mod.deep_update({'a': 1, 'b': 3}, {'b': {'c': 4}})
    assert result == {'a': 1, 'b': {'c': 4}}, (
        'Dictionaries should be a merge of the originals'
    )


@mark.issue(id=7)
@mark.unit
def test_deep_update_update_nested_dict_new_keys():
    result = mod.deep_update({'a': 1, 'b': {'c': 1}}, {'b': {'d': 4, 'e': 5}})
    assert result == {'a': 1, 'b': {'c': 1, 'd': 4, 'e': 5}}, (
        'Dictionaries should be a merge of the originals'
    )


@mark.issue(id=7)
@mark.unit
def test_parse_bases_no_bases():
    result = mod.parse_bases({'a': 1, 'b': 2})
    assert result == {'a': 1, 'b': 2}, 'No bases in object means it should pass through'


@mark.issue(id=7)
@mark.unit
def test_parse_bases_ref_base_same_file():
    mod.DOCUMENTS.current_file = Path('project.yaml')
    link = mod.DocumentLink('project.yaml', 1)
    mod.DOCUMENTS.add_document(link, {'a': 1, 'b': 2})
    mod.DOCUMENTS.add_tag('ref', 'link', link)

    result = mod.parse_bases({'bases': [{'ref': 'link'}], 'c': 3, 'a': 4})
    assert result == {'a': 4, 'b': 2, 'c': 3}, (
        'Return should be a merge of two documents'
    )


@mark.issue(id=7)
@mark.unit
def test_parse_bases_ref_base_different_file(monkeypatch):
    mod.DOCUMENTS.current_file = Path('project.yaml')
    link = mod.DocumentLink('other_project.yaml', 0)
    mod.DOCUMENTS.add_document(link, {'a': 1, 'b': 2})
    mod.DOCUMENTS.add_tag('ref', 'link', link)
    monkeypatch.setattr(Path, 'exists', lambda _: True)

    result = mod.parse_bases({'bases': [{'ref': 'link'}], 'c': 3, 'a': 4})
    assert result == {'a': 4, 'b': 2, 'c': 3}, (
        'Return should be a merge of two documents'
    )


@mark.issue(id=7)
@mark.unit
def test_parse_bases_path_base_same_file(monkeypatch):
    mod.DOCUMENTS.current_file = Path('project.yaml')
    link = mod.DocumentLink('project.yaml', 1)
    mod.DOCUMENTS.add_document(link, {'a': 1, 'b': 2})
    monkeypatch.setattr(Path, 'exists', lambda _: True)

    result = mod.parse_bases(
        {'bases': [{'path': 'project.yaml', 'index': 1}], 'c': 3, 'a': 4}
    )
    assert result == {'a': 4, 'b': 2, 'c': 3}, (
        'Return should be a merge of two documents'
    )


@mark.issue(id=7)
@mark.unit
def test_parse_bases_path_base_default_file(monkeypatch):
    mod.DOCUMENTS.current_file = Path('project.yaml')
    link = mod.DocumentLink('project.yaml', 1)
    mod.DOCUMENTS.add_document(link, {'a': 1, 'b': 2})
    monkeypatch.setattr(Path, 'exists', lambda _: True)

    result = mod.parse_bases({'bases': [{'index': 1}], 'c': 3, 'a': 4})
    assert result == {'a': 4, 'b': 2, 'c': 3}, (
        'Return should be a merge of two documents'
    )


@mark.issue(id=7)
@mark.unit
def test_parse_bases_path_base_default_file_only_dict():
    mod.DOCUMENTS.current_file = Path('project.yaml')
    link = mod.DocumentLink('project.yaml', 1)
    mod.DOCUMENTS.add_document(link, {'a': 1, 'b': 2})

    result = mod.parse_bases({'bases': {'index': 1}, 'c': 3, 'a': 4})
    assert result == {'a': 4, 'b': 2, 'c': 3}, (
        'Return should be a merge of two documents'
    )


@mark.issue(id=7)
@mark.unit
def test_parse_bases_invalid_path_reference():
    mod.DOCUMENTS.current_file = Path('project.yaml')
    link = mod.DocumentLink('project.yaml', 1)
    mod.DOCUMENTS.add_document(link, {'a': 1, 'b': 2})

    with raises(ValueError) as exc:
        _ = mod.parse_bases(
            {'bases': [{'path': 'missing.yaml', 'index': 1}], 'c': 3, 'a': 4}
        )

    assert exc.type is ValueError, 'Invalid file should return a ValueError'
    assert exc.value.args[0] == 'Path to Object Reference does not exist'
    assert isinstance(exc.value.args[1], dict), (
        'Exception should return additional information about the error'
    )
