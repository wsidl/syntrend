from syntrend.config.model import constants

from pathlib import Path
from typing import Callable, Any


class DocumentLink:
    def __init__(self, target_path: Path | str, index: int):
        if isinstance(target_path, str):
            target_path = DOCUMENTS.current_dir.joinpath(target_path)
        self.path = target_path
        self.index = index

    def __hash__(self):
        return hash((self.path, self.index))

    def __repr__(self):
        return f'<DocumentLink path={repr(self.path)} index={self.index}>'

    def working_directory(self):
        return self.path.parent

    def get_reference(self):
        if self not in DOCUMENTS:
            DOCUMENTS.retrieve(self.path)
        return DOCUMENTS.get_document(self)


class DocumentCollection:
    def __init__(self):
        self.__tags: dict[tuple[str, str], DocumentLink] = {}
        self.__sources: dict[int, Any] = {}
        self.__retriever = lambda x: None
        self.current_dir: Path | None = None

    def clear(self):
        self.__tags = {}
        self.__sources = {}
        self.__retriever = lambda x: None

    def add_document(self, link: DocumentLink, content):
        self.__sources[hash(link)] = content

    def add_tag(self, tag_type: str, tag_value: str, link: DocumentLink):
        self.__tags[(tag_type, tag_value)] = link

    def get_tag(self, tag_type: str, tag_value: str):
        tag_link = self.__tags[(tag_type, tag_value)]
        return self.get_document(tag_link)

    def iter_tags(self, tag_type: str):
        for _tag_type, tag_value in self.__tags:
            if _tag_type == tag_type:
                yield tag_value, self.__tags[(_tag_type, tag_value)]

    def iter_documents(self):
        for doc in self.__sources.values():
            yield doc

    def get_document(self, link: DocumentLink):
        if hash(link) not in self.__sources:
            self.retrieve(link.path)
        return self.__sources[hash(link)]

    def get_reference(self, reference: str):
        if match := constants.RE_BASE_REF_DOC.fullmatch(reference):
            ref_name = match.group(1)
            return self.get_tag('ref', ref_name)
        if match := constants.RE_BASE_LINK_DOC.fullmatch(reference):
            path_ref, index = match.groups()
            link = DocumentLink(self.current_dir.joinpath(path_ref), int(index or 0))
            return self.get_document(link)

    def set_retriever(self, func: Callable[[list[dict] | dict | str | Path], None]):
        self.__retriever = func

    def retrieve(self, path: list[dict] | dict | str | Path):
        self.__retriever(path)

    def __contains__(self, item: tuple[str, str] | DocumentLink) -> bool:
        if isinstance(item, DocumentLink):
            return hash(item) in self.__sources
        return item in self.__tags


DOCUMENTS = DocumentCollection()
ROOT_DOC = {}
