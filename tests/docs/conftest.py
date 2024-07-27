from pathlib import Path
import re

from click.testing import CliRunner
from pytest import fixture

RE_BLOCK_START = re.compile(r'^\[[^]]*test_name="?([^"]*)"?[^]]*]$')
RE_INTERN_BLOCK = re.compile(r'^\| \[source, ?([a-z]+)]\n-{4,}\n((.|\n)*?)\n-{4,}$', re.MULTILINE)
RE_TABLE_DELIM = re.compile(r'^\|={3,}$')


@fixture(scope="function")
def load_doc(request, monkeypatch):
    from syntrend.__main__ import generate

    name = request.node.name.split("_", 1)[1]

    def __parse_doc_config(src_file: str):
        pth = Path(src_file)
        table_buffer = []
        buffer_type = ""
        # get table
        with pth.open("r") as ad:
            for line in ad:
                _line = line[:-1]
                if not _line:
                    continue
                if RE_TABLE_DELIM.fullmatch(_line):
                    match = RE_BLOCK_START.fullmatch(last_line)
                    if match:
                        if match.group(1) == name:
                            buffer_type = "table"
                        continue
                    elif buffer_type == "table":
                        break
                if buffer_type == "table":
                    table_buffer.append(_line)
                last_line = _line

        _table_buffer = "\n".join(table_buffer)
        blocks = {}
        for block in RE_INTERN_BLOCK.finditer(_table_buffer):
            blocks[block.group(1)] = block.group(2)
        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            test_config = Path("test.yml")
            with test_config.open("w") as out:
                out.write(blocks.pop("yaml").replace("\\|", "|") + "\n")
            cli_result = runner.invoke(generate, [str(test_config.absolute())])
        response = (
            blocks.pop("console").split("\n", 1)[1],
            cli_result,
        )
        return response

    return __parse_doc_config
