from syntrend.config import CONFIG

from typing import Any, Callable
from pathlib import Path
import sys
from os import linesep

T_Event_Callback = Callable[[None], Any]
BASE_OUTPUT_CONFIG = CONFIG.output
STREAM_TARGET_FILE = 'stream_file'
STREAM_TARGET_CONSOLE = 'stream_console'
CONSOLE_DEFAULT_EVENT_FORMAT = '{body}'
CONSOLE_DEFAULT_COLLECTION_FORMAT = '{body}'


class OutputHandler:
    def __init__(self, object_name: str):
        self.object_def = CONFIG.objects[object_name]
        self.object_name = object_name
        self.args = {}

    def load(self):
        return

    def write(self, event: str, clear=False) -> None:
        return

    def close(self) -> None:
        return


class ConsoleHandler(OutputHandler):
    def load(self):
        args = {
            'name': self.object_name,
            'buffer': '',
            'body': '{body}',
            'nl': linesep,
        }
        if self.object_def.output.collection:
            out_format = self.object_def.output.kwargs.get(
                'console_collection_format',
                CONSOLE_DEFAULT_COLLECTION_FORMAT,
            )
        else:
            longest_name = max([len(obj_name) for obj_name in CONFIG.objects])
            args['buffer'] = ' ' * (longest_name - len(self.object_name) + 1)
            out_format = self.object_def.output.kwargs.get(
                'console_event_format', CONSOLE_DEFAULT_EVENT_FORMAT
            )
        self.args['format'] = out_format.format(**args)

    def write(self, content: str, clear=False) -> None:
        sys.stdout.write(self.args['format'].format(body=content))


class FileHandler(OutputHandler):
    def load(self):
        self.args['sequence'] = 0
        self.args['path'] = Path(self.object_def.output.directory).joinpath(
            self.object_def.output.filename_format.format(
                name=self.object_name,
                format=self.object_def.output.format,
                id='{id}',
            )
        )

    def write(self, content: str, clear=False):
        self.args['sequence'] += 1
        file_path = Path(str(self.args['path']).format(id=self.args['sequence']))
        if clear:
            file_path.unlink(missing_ok=True)
        if not file_path.exists():
            file_path.open(mode='x')
        with file_path.open(mode='r+b') as f:
            f.write(content.encode('utf-8'))


def setup_event_stream(object_name: str) -> OutputHandler:
    output_config = CONFIG.objects[object_name].output
    if output_config.directory and str(output_config.directory) != '-':
        handler = FileHandler(object_name)
    else:
        handler = ConsoleHandler(object_name)
    handler.load()

    return handler
