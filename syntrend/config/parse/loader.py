from syntrend.config.parse.parser import yaml
from syntrend.config.parse.parse_func import parse_object
from syntrend.config import model

from pathlib import Path

from ruamel.yaml import error

ROOT_TAG = ('pos', '.')


def retrieve_source(config_file: list[dict] | dict | str | Path) -> None:
    if isinstance(config_file, list | dict):
        model.DOCUMENTS.add_document(
            model.DocumentLink(Path.cwd().joinpath('main'), 0),
            config_file,
        )
        return

    content = config_file
    if (path_ref := Path(config_file).absolute()).exists():
        with path_ref.open('r') as file_obj:
            content = file_obj.read()
        config_file = path_ref
        if path_ref.is_relative_to(Path.cwd()):
            config_file = path_ref.relative_to(Path.cwd())
    try:
        model.DOCUMENTS.current_file = config_file
        for index, doc in enumerate(yaml.load_all(content)):
            doc_link = model.DocumentLink(config_file, index)
            model.DOCUMENTS.add_document(doc_link, doc)

            if model.constants.OBJ_REF_TAG in doc:
                ref_value = doc.pop(model.constants.OBJ_REF_TAG)
                if ('ref', ref_value) in model.DOCUMENTS:
                    file_ref = model.DOCUMENTS.file_references[('ref', ref_value)]
                    raise KeyError(
                        'Provided Project Reference already exists',
                        {
                            'Reference Name': ref_value,
                            'File of Existing Reference': str(file_ref.path),
                            'Document Index in File': file_ref.index,
                        },
                    ) from None
                model.DOCUMENTS.add_tag('ref', ref_value, doc_link)
                continue
            if model.constants.OBJ_POS_TAG in doc:
                pos_value = doc.pop(model.constants.OBJ_POS_TAG)
                if ('pos', pos_value) in model.DOCUMENTS:
                    file_ref = model.DOCUMENTS.file_references[('pos', pos_value)]
                    raise KeyError(
                        'Provided Object Position already exists',
                        {
                            'Reference Name': 'root' if pos_value == '.' else pos_value,
                            'File of Existing Object': str(file_ref.path),
                            'Document Index in File': file_ref.index,
                        },
                    ) from None
                model.DOCUMENTS.add_tag('pos', pos_value, doc_link)
                continue

    except error.YAMLError as err:
        raise ValueError(
            f'Invalid content format provided for parsing - {type(err).__name__}: {err.args}',
            {'File Header': content[:40].replace('\n', '\\n')},
        ) from err


def load_config(config_file: dict | str | Path) -> model.ProjectConfig:
    # Reset Documents Global
    model.DOCUMENTS.clear()
    model.DOCUMENTS.set_retriever(retrieve_source)
    model.DOCUMENTS.retrieve(config_file)

    # Locate Project Root
    if ROOT_TAG in model.DOCUMENTS:
        doc = model.DOCUMENTS.get_tag(*ROOT_TAG)
        parsed_obj = parse_object(doc)
        if isinstance(parsed_obj, model.ProjectConfig):
            return parsed_obj
        raise TypeError(
            'Provided `!syntrend/root` Document does not provide a Project Root',
            {'Parsed Type': type(parsed_obj).__name__, 'content': doc},
        )
    else:
        new_config = model.ProjectConfig(objects={'this': {'type': 'string'}})
        for document in model.DOCUMENTS.iter_documents():
            parsed_doc = parse_object(document)
            if isinstance(parsed_doc, model.ProjectConfig):
                return parsed_doc

    # Parse all other documents
    for doc in model.DOCUMENTS.iter_documents():
        parsed_obj = parse_object(doc)
        if isinstance(parsed_obj, model.ProjectConfig):
            return parsed_obj

        if isinstance(parsed_obj, model.ModuleConfig):
            new_config.config.update_(parsed_obj)
            continue

        if isinstance(parsed_obj, model.PropertyDefinition | model.ObjectDefinition):
            new_config.objects['this'] = parsed_obj
            continue

        if isinstance(doc, dict):
            for doc_key in doc:
                parsed_sub = parse_object(doc[doc_key])
                if isinstance(
                    parsed_sub, model.PropertyDefinition | model.ObjectDefinition
                ):
                    new_config.objects[doc_key] = parsed_sub

    return new_config
