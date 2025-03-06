import sys
from traceback import print_tb
from os import linesep, environ


def process_exception(e: Exception):
    lines = [f'Error Encountered: ({getattr(e, "name", type(e).__name__)})']
    for arg in e.args:
        if isinstance(arg, dict):
            for k in arg:
                lines.append(f'  | {k}: {arg[k]}')
        else:
            lines.append(f'  | {arg}')
    sys.stderr.write(linesep.join(lines) + linesep)
    if environ.get('SYNTREND_DEBUG', 0):
        print_tb(e.__traceback__, file=sys.stderr)
    sys.exit(1)
