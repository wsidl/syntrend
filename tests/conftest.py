from pytest import fixture

import logging


@fixture(autouse=True)
def set_debug_log_level(caplog):
    caplog.set_level(logging.DEBUG)
