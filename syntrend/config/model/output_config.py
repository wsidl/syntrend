from syntrend.config.model.base_config import Validated, dc, dataclass
from syntrend.config.model.constants import OUTPUT_STDOUT, DEFAULT_FILE_FORMAT
from pathlib import Path


@dataclass
class OutputConfig(Validated):
    """Configuration Properties used for Global and Object-specific outputs"""

    format: str = dc.field(default='json')
    directory: Path = dc.field(default='-')
    filename_format: str = dc.field(default=DEFAULT_FILE_FORMAT)
    collection: bool = dc.field(default=False)
    count: int = dc.field(default=1)
    time_field: str = dc.field(default='')

    def parse_collection(self, value):
        return bool(value)

    def parse_directory(self, value):
        if isinstance(value, Path):
            return value
        if value == '-':
            return OUTPUT_STDOUT
        p = Path(value).absolute()
        if not p.exists():
            p.mkdir(parents=True)
        assert p.is_dir(), 'Path must be a directory'
        return p

    def validate_(self):
        if self.collection and self.time_field:
            raise ValueError(
                'Cannot create a collection when time simulation is being used',
                {
                    'Collection': self.collection,
                    'Time Field': self.time_field,
                    'Format': self.format,
                },
            )
