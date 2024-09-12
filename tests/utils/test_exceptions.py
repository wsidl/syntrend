from syntrend.utils import exc
from os import linesep


def test_exception_output(monkeypatch):
    reported_exception = [0]
    reported_output = ['']

    def _exit_code(code: int):
        reported_exception[0] = code

    def _error_output(content: str):
        reported_output[0] = content

    monkeypatch.setattr(exc.sys, 'exit', _exit_code)
    monkeypatch.setattr(exc.sys.stderr, 'write', _error_output)
    err = ValueError('Failed Expression', {"a": 1, "b": 2, "c": 3})
    exc.process_exception(err)

    assert (
        reported_exception[0] == 1
    ), 'Reported error exit code should be 2 (Expression Error)'
    assert (
        reported_output[0]
        == linesep.join(
            [
                'Error Encountered: (ValueError)',
                '  | Failed Expression',
                '  | a: 1',
                '  | b: 2',
                '  | c: 3',
            ]
        )
        + linesep
    ), 'Exception output format not meeting expected format'
