from pathlib import Path
from typing import Callable, Any


class DocumentReference:
    def __init__(self, ref: str, path: Path, index: int):
        self.ref = ... if not ref else ref
        self.path = path
        self.index = index

    def get_reference(self):
        if self.ref is not ...:
            return DOCUMENTS.get_tag('ref', self.ref)

    @classmethod
    def load(cls, **kwargs) -> 'DocumentReference':
        ref = kwargs.pop('ref', ...)
        if not (path := Path(kwargs.pop('path', ''))).is_file():
            path = DOCUMENTS.current_file.parent.joinpath(path)
        index = int(kwargs.pop('index', 0))
        return cls(ref, path, index)


class DocumentLink:
    def __init__(self, target_path: Path | str, index: int):
        if isinstance(target_path, str):
            target_path = DOCUMENTS.current_file.parent.joinpath(target_path)
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
        self.current_file: Path | None = None

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

    def get_reference(self, reference: dict):
        if reference.get('ref', ...) is not ...:
            return self.get_tag('ref', reference['ref'])
        if 'path' in reference:
            link = DocumentLink(
                self.current_file.parent.joinpath(reference['path']),
                int(reference.get('index', 0)),
            )
            return self.get_document(link)
        if 'index' in reference:
            link = DocumentLink(self.current_file, int(reference.get('index', 0)))
            return self.get_document(link)
        raise ValueError(
            'Provided Reference is not valid to retrieve documents',
            {
                'reference': str(reference),
                'expected keys': 'ref, path, and/or index',
            },
        )

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
