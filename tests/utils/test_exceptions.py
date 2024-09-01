from syntrend.utils import exceptions
from os import linesep


def test_exception_output(monkeypatch):
    reported_exception = [0]
    reported_output = ['']

    def _exit_code(code: int):
        reported_exception[0] = code

    def _error_output(content: str):
        reported_output[0] = content

    monkeypatch.setattr(exceptions.sys, 'exit', _exit_code)
    monkeypatch.setattr(exceptions.sys.stderr, 'write', _error_output)
    exc = exceptions.ExpressionError('Failed Expression', 1, 2, 3)
    exceptions.process_exception(exc)

    assert (
        reported_exception[0] == 2
    ), 'Reported error exit code should be 2 (Expression Error)'
    assert (
        reported_output[0]
        == linesep.join(
            [
                'Error Encountered: (Expression Error)',
                '  | Failed Expression',
                '  | 1',
                '  | 2',
                '  | 3',
            ]
        )
        + linesep
    ), 'Exception output format not meeting expected format'
