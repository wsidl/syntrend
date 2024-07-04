from event_gen.config import model

from contextlib import contextmanager
from typing import Callable, Union
from pathlib import Path
from io import BufferedRandom, RawIOBase, SEEK_END, StringIO
from sys import stdout

T_Primary = Union[str, int, float, dict[str, "T_Primary"]]
T_Formatter = Callable[[T_Primary], str]
T_Writer = Callable[[RawIOBase, str], str]


def json_formatter(cfg: model.OutputConfig) -> tuple[T_Formatter, T_Writer]:
    import json

    def _formatter(event: T_Primary) -> str:
        return json.dumps(event)

    def _writer(out_stream: RawIOBase, event: str) -> str:
        output_string = event
        if cfg.aggregate and out_stream.seekable():
            out_stream.seek(0, SEEK_END)
            if out_stream.tell() == 0:
                output_string = f"[\n\t{event}\n]"
            else:
                output_string = f",\n\t{event}\n]"
                out_stream.seek(-2, SEEK_END)
        else:
            output_string += "\n"
        return output_string

    return _formatter, _writer


def csv_formatter(cfg: model.OutputConfig) -> tuple[T_Formatter, T_Writer]:
    import csv
    _columns = []
    _buffer = StringIO()
    _csvwriter = csv.DictWriter(_buffer, [])
    _record_header = []

    def _formatter(event: T_Primary) -> str:
        _buffer.seek(0)
        _buffer.truncate()
        if not isinstance(event, dict):
            event = {"value": event}
        if not _csvwriter.fieldnames:
            _csvwriter.fieldnames = list(event.keys())
        _csvwriter.writeheader()
        _csvwriter.writerow(event)
        return _buffer.getvalue()

    def _writer(out_stream: RawIOBase, event: str) -> str:
        header, row, _ = event.replace("\r", "").split("\n")
        if out_stream.seekable():
            out_stream.seek(0, SEEK_END)
        output_string = ""
        if not cfg.aggregate or not _record_header:
            output_string += f"{header}\n"
        output_string += f"{row}\n"
        if not _record_header:
            _record_header.append(header)
        return output_string

    return _formatter, _writer


FORMATS: dict[str, Callable[[model.OutputConfig], tuple[T_Formatter, T_Writer]]] = {
    "csv": csv_formatter,
    "json": json_formatter,
}
OUTPUT_COUNTS: dict[str, int] = {}


def load_formatter(object_name: str, output_cfg: model.OutputConfig):
    assert output_cfg.output_format in FORMATS, f'Format "{output_cfg.output_format}" is not supported'
    __formatter, __writer = FORMATS[output_cfg.output_format](output_cfg)
    format_cfg = {
        "name": object_name,
        "format": output_cfg.output_format,
        "id": "{id}"
    }
    output_dir = None
    output_path = ""
    if str(output_cfg.output_dir) != "-":
        output_dir = Path(output_cfg.output_dir)
        output_path = output_dir.joinpath(output_cfg.filename_format.format(**format_cfg))
    count_key = str(output_path)
    if count_key not in OUTPUT_COUNTS:
        OUTPUT_COUNTS[count_key] = 0

    @contextmanager
    def _ctx_opener():
        if not output_dir:
            yield stdout
            return
        else:
            seq = 0
            if not output_cfg.aggregate:
                OUTPUT_COUNTS[count_key] += 1
                seq = OUTPUT_COUNTS[count_key]
            _out = Path(count_key.format(id=seq))
            if not _out.exists():
                _out.open(mode="x")
            with _out.open(mode="r+b") as f:
                yield f

    def __run_formatter(event: T_Primary):
        value = __formatter(event)
        with _ctx_opener() as out_stream:
            output_string = __writer(out_stream, value)
            if isinstance(out_stream, BufferedRandom):
                output_string = output_string.encode("utf-8")
            out_stream.write(output_string)

    return __run_formatter
