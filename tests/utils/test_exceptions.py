from syntrend.utils import exc
from pytest import mark
from os import linesep


@mark.unit
def test_exception_output(monkeypatch):
    dummy_exception = exc.ExceptionHandler(None, None, False)
    monkeypatch.setattr(exc, 'EXCEPTION_HANDLER', dummy_exception)
    err = ValueError('Failed Expression', {'a': 1, 'b': 2, 'c': 3})
    exc.EXCEPTION_HANDLER.error(err)
    monkeypatch.undo()

    assert dummy_exception.exit_code == 1, (
        'Reported error exit code should be 2 (Expression Error)'
    )
    assert (
        dummy_exception.stderr_output
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
