from syntrend.config import CONFIG
from syntrend.utils import writers

from pathlib import Path
from tempfile import mkstemp
from typing import Callable, Union
from os import close, linesep
from importlib import import_module
import pickle
import logging
import sys
from collections import namedtuple

LOG = logging.getLogger(__name__)
T_Primary = Union[str, int, float, dict[str, 'T_Primary']]
Formatter = namedtuple('Formatter', 'format,close')
T_Formatter = Callable[[str], Callable[['Collection'], list[str]]]
FORMATTERS: dict[str, T_Formatter] = {}

STREAM_FEED_EVENT = 'stream_event'
STREAM_FEED_COLLECTION = 'stream_collection'
TH_TEMP_PATH = 'temp_path'

FORMAT_FIELDS_DEFAULT = {
    'nl': linesep,
}


class Event(dict):
    def __init__(self, value):
        self.use_default = False
        if not isinstance(value, dict):
            value = {'value': value}
            self.use_default = True
        super().__init__(**value)


class Collection(list):
    def __init__(self, *events: Event):
        super().__init__(events)


class TempHandler(writers.OutputHandler):
    def load(self):
        fd, temp_path = mkstemp(prefix='syntrend_')
        close(fd)
        self.args[TH_TEMP_PATH] = Path(temp_path)
        self.args['output_callback'] = lambda x: None

    def write(self, event: Event, _=False):
        if (
            self.args[TH_TEMP_PATH].exists()
            and self.args[TH_TEMP_PATH].stat().st_size > 0
        ):
            with open(self.args[TH_TEMP_PATH], 'rb') as t_file:
                _buffer = pickle.load(t_file)
        else:
            _buffer = Collection()
        _buffer.append(event)
        with open(self.args[TH_TEMP_PATH], 'wb') as t_file:
            pickle.dump(_buffer, t_file)

    def get_collection(self) -> Collection:
        with open(self.args[TH_TEMP_PATH], 'r+b') as t_file:
            return pickle.load(t_file)

    def close(self):
        self.args[TH_TEMP_PATH].unlink(missing_ok=True)


def register_formatter(format_name: str):
    if format_name in FORMATTERS:
        raise NameError(
            'Formatter is already registered', {'Formatter Name': format_name}
        )

    def _register_formatter(func: T_Formatter):
        FORMATTERS[format_name] = func
        return func

    return _register_formatter


def load_formatter(object_name: str) -> Formatter:
    output_config = CONFIG.objects[object_name].output
    output_handler = writers.setup_event_stream(object_name)
    formatter = FORMATTERS[output_config.format](object_name)

    if output_config.collection:
        temp_collector = TempHandler(object_name)
        temp_collector.load()
    else:
        temp_collector = writers.OutputHandler(object_name)

    def __handle_events(event: dict):
        clear_target = False
        event = Event(event)
        if output_config.collection:
            temp_collector.write(event)
            return
        event = Collection(event)
        formatted_output = formatter(event)
        output_handler.write(linesep.join(formatted_output) + linesep, clear_target)

    def __handle_close():
        if output_config.collection:
            events = temp_collector.get_collection()
            formatted_output = formatter(events)
            output_handler.write(linesep.join(formatted_output) + linesep)
        temp_collector.close()
        output_handler.close()

    return Formatter(__handle_events, __handle_close)


def _load_formatter_dir(module_name: str, directory: Path):
    for _file in directory.iterdir():
        if (
            not _file.suffix.startswith('.py')
            or _file.is_dir()
            or _file.name.startswith('_')
        ):
            continue
        basename = _file.name.split('.')[0]
        _ = import_module(f'{module_name}.{basename}')


def load_formatters():
    _load_formatter_dir('syntrend.formatters', Path(__file__).parent)
    if not CONFIG.config.formatter_dir:
        return
    add_formatter_pkg = Path(CONFIG.config.formatter_dir).absolute()
    if not (add_formatter_pkg.is_dir() and add_formatter_pkg.exists()):
        return
    formatter_pkg_name = add_formatter_pkg.name
    sys.path.append(str(add_formatter_pkg))
    _load_formatter_dir(formatter_pkg_name, add_formatter_pkg)
