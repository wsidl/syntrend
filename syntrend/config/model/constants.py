from pathlib import Path
import re

OBJ_REF_TAG = '_st_ref'
OBJ_POS_TAG = '_st_pos'

DEFAULT_ENV_VAR_PREFIX = 'SYNTREND_'
DEFAULT_FILE_FORMAT = '{name}-{id}.{format}'

RE_BASE_LINK_DOC = re.compile(r'(.*\..*)(?: (\d+))?')
RE_BASE_REF_DOC = re.compile(r'ref::(.*)')
OUTPUT_STDOUT = Path('-')
USER_CONFIG_DIR = Path.home().joinpath('.config', 'syntrend')
ADD_GENERATOR_DIR = USER_CONFIG_DIR.joinpath('generators')
