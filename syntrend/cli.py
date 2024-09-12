import click
import pathlib

from syntrend import generators, formatters
from syntrend.utils import manager, exc
from syntrend.config import load_config

ERRORS = []


def error(message):
    global ERRORS
    if message not in ERRORS:
        ERRORS.append(message)


@click.group(name='app')
def app():
    pass


@app.command()
@click.argument('project_file', nargs=1, type=click.Path(exists=True))
def generate(project_file: pathlib.Path):
    """
    Uses the available project file to generate datasets
    """
    try:
        load_config(project_file)
        generators.load_generators()
        formatters.load_formatters()
        manager.ROOT_MANAGER.load()
        manager.ROOT_MANAGER.start()
    except Exception as e:
        exc.process_exception(e)


@app.command()
@click.argument('project_file', nargs=1, type=click.Path(exists=True))
def validate(config_file: pathlib.Path):
    """
    Validates and summarizes a project file
    """
    pass


if __name__ == '__main__':
    app()
