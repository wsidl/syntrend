import sys
from traceback import format_tb
from os import linesep, environ


class ExceptionHandler(SystemExit):
    def __init__(self, sys_stderr, sys_exit, _raise=True):
        self.__stderr = sys_stderr
        self.stderr = []
        self.stderr_output = ''
        self.__exit = sys_exit
        self.exit_code = 0
        self.exception = None
        self.__raise = _raise

    def error(self, exc: Exception) -> None:
        lines = [f'Error Encountered: ({getattr(exc, "name", type(exc).__name__)})']
        for arg in exc.args:
            if isinstance(arg, dict):
                for k in arg:
                    lines.append(f'  | {k}: {arg[k]}')
            else:
                lines.append(f'  | {arg}')
        self.stderr += lines
        if environ.get('SYNTREND_DEBUG', 0):
            self.stderr += [''] + [
                sub_line
                for line in format_tb(exc.__traceback__)
                for sub_line in line.split(linesep)
                if sub_line.strip()
            ]
        self.exit_code = 1
        self.stderr_output = linesep.join(self.stderr) + linesep
        if self.__raise:
            self.__stderr.write(self.stderr_output)
            self.__exit(self.exit_code)


EXCEPTION_HANDLER = ExceptionHandler(sys.stderr, sys.exit)
