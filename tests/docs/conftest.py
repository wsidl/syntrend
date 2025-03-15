from pathlib import Path
import re

from click.testing import CliRunner, Result
from pytest import fixture

RE_BLOCK_START = re.compile(r'^\[[^]]*test_name="?([^"]*)"?[^]]*]$')
RE_INTERN_BLOCK = re.compile(
    r'^\| \[source, ?([a-z]+)]\n-{4,}\n((.|\n)*?)\n-{4,}$', re.MULTILINE
)
RE_TABLE_DELIM = re.compile(r'^\|={3,}$')


@fixture(scope='function')
def project_result(request, monkeypatch) -> Result:
    from syntrend.cli import generate, exc
    import sys

    dummy_exception = exc.ExceptionHandler(None, None, False)
    monkeypatch.setattr(exc, 'EXCEPTION_HANDLER', dummy_exception)
    name = request.node.name.split('_', 1)[1]
    runner = CliRunner(mix_stderr=False)
    test_config = Path.cwd().joinpath(f'tests/assets/uc_{name}.yaml').absolute()
    with runner.isolated_filesystem():
        cli_result = runner.invoke(
            generate, [str(test_config)], env={'SYNTREND_DEBUG': '1'}
        )

    monkeypatch.undo()
    if dummy_exception.exit_code:
        cli_result.exit_code = dummy_exception.exit_code
        print(dummy_exception.stderr_output, file=sys.stderr)
    return cli_result
