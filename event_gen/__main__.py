import click
import pathlib

from event_gen import generators
from event_gen.config import load_config, CONFIG

ERRORS = []


def error(message):
    global ERRORS
    if message not in ERRORS:
        ERRORS.append(message)


@click.group(name="app")
def _app():
    pass


@_app.command()
@click.argument("project_file", nargs=1, type=click.Path(exists=True))
def generate(project_file: pathlib.Path):
    """
    Uses the available project file to generate datasets
    """
    load_config(project_file)
    generators.manager.ROOT_MANAGER.load()
    generators.manager.ROOT_MANAGER.start()

    # configs = []
    # schemas = {}
    # for arg in inputs:
    #     if "=" in arg:
    #         schema, schema_file_name = arg.split("=")
    #         schema_file = pathlib.Path(schema_file_name)
    #         if not schema_file.exists():
    #             error(f'Schema File "{schema_file_name}" does not exist')
    #             continue
    #         if schema in schemas:
    #             error(f'Schema "{schema}" has already been provided')
    #             continue
    #         schemas[schema] = schema_file
    #     else:
    #         config_file = pathlib.Path(arg)
    #         if not config_file.exists():
    #             error(f'Config File "{arg}" does not exist')
    #             continue
    #         configs.append(config_file)
    # if ERRORS:
    #     click.echo(
    #         "Cannot generate any events until the following issues are resolved",
    #         err=True,
    #     )
    #     for e in ERRORS:
    #         click.echo(f" - {e}", err=True)


@_app.command()
@click.argument("project_file", nargs=1, type=click.Path(exists=True))
def validate(config_file: pathlib.Path):
    """
    Validates and summarizes a project file
    """
    pass


if __name__ == "__main__":
    _app()
