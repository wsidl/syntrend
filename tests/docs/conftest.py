from pathlib import Path
import re
import traceback

from click.testing import CliRunner, Result
from pytest import fixture

RE_BLOCK_START = re.compile(r'^\[[^]]*test_name="?([^"]*)"?[^]]*]$')
RE_INTERN_BLOCK = re.compile(r'^\| \[source, ?([a-z]+)]\n-{4,}\n((.|\n)*?)\n-{4,}$', re.MULTILINE)
RE_TABLE_DELIM = re.compile(r'^\|={3,}$')


@fixture(scope="function")
def project_result(request, monkeypatch) -> Result:
    from syntrend.__main__ import generate

    name = request.node.name.split("_", 1)[1]
    runner = CliRunner(mix_stderr=False)
    test_config = Path(f"tests/assets/uc_{name}.yaml").absolute()
    with runner.isolated_filesystem():
        cli_result = runner.invoke(generate, [str(test_config)])
    if cli_result.exit_code:
        traceback.print_tb(cli_result.exc_info[2])
    return cli_result
