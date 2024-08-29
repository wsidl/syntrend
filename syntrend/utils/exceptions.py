import sys
from os import linesep


class ProcessException(Exception):
    name = "General Error"
    code = -1


class ExpressionError(ProcessException):
    name = "Expression Error"
    code = 2


def process_exception(e: ProcessException):
    sys.stderr.write(linesep.join([f"Error Encountered: ({e.name})"] + [f"  | {line}" for line in e.args]) + linesep)
    sys.exit(e.code)
