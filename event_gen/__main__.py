import click
import pathlib

ERRORS = []


def error(message):
    global ERRORS
    if message not in ERRORS:
        ERRORS.append(message)


@click.command()
@click.argument("config", nargs=1)
def generate(inputs: list[str]):
    configs = []
    schemas = {}
    for arg in inputs:
        if "=" in arg:
            schema, schema_file_name = arg.split("=")
            schema_file = pathlib.Path(schema_file_name)
            if not schema_file.exists():
                error(f'Schema File "{schema_file_name}" does not exist')
                continue
            if schema in schemas:
                error(f'Schema "{schema}" has already been provided')
                continue
            schemas[schema] = schema_file
        else:
            config_file = pathlib.Path(arg)
            if not config_file.exists():
                error(f'Config File "{arg}" does not exist')
                continue
            configs.append(config_file)
    if ERRORS:
        click.echo(
            "Cannot generate any events until the following issues are resolved",
            err=True,
        )
        for e in ERRORS:
            click.echo(f" - {e}", err=True)
