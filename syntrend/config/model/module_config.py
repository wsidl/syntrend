from syntrend.config.model.base_config import Validated, dc, dataclass, parse_int
from syntrend.config.model.constants import DEFAULT_ENV_VAR_PREFIX, ADD_GENERATOR_DIR
from os import getenv
from pathlib import Path


@dataclass
class ModuleConfig(Validated):
    """Configuration Properties to modify/alter how the `syntrend` utility behaves"""

    max_generator_retries: int = dc.field(
        default=int(getenv(f'{DEFAULT_ENV_VAR_PREFIX}_MAX_GENERATOR_RETRIES', 20))
    )
    """Maximum number of retries a Generator can perform before failing."""
    max_historian_buffer: int = dc.field(
        default=int(getenv(f'{DEFAULT_ENV_VAR_PREFIX}_MAX_HISTORIAN_BUFFER', 20))
    )
    """Maximum values to be kept in a buffer of previous values"""
    generator_dir: str = dc.field(
        default=getenv(f'{DEFAULT_ENV_VAR_PREFIX}_GENERATOR_DIR', '')
    )
    """Source Directory of Custom Generators"""
    formatter_dir: str = dc.field(
        default=getenv(f'{DEFAULT_ENV_VAR_PREFIX}_FORMATTERS_DIR', '')
    )
    """Source Directory of Custom Formatters"""

    parse_max_generator_retries = parse_int(_min=1)
    parse_max_historian_buffer = parse_int(_min=1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def parse_generator_dir(self, value: str) -> Path:
        if not value:
            return ADD_GENERATOR_DIR
        parsed_path = Path(value).absolute()
        if not parsed_path.is_dir():
            raise ValueError(
                'Source Generator Directory does not exist',
                {
                    'Input Path': value,
                    'Parsed Path': str(parsed_path),
                },
            )
        return parsed_path
