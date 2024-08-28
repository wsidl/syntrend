from syntrend.formatters import register_formatter, Collection
from syntrend.config import CONFIG

DEFAULT_LINESEP = "\r\n"


@register_formatter('csv')
def csv_formatter(object_name: str):
    import csv
    from io import StringIO
    buffer = StringIO()
    csv_writer = csv.DictWriter(buffer, {}, quoting=csv.QUOTE_NONNUMERIC)
    output_options = CONFIG.objects[object_name].output

    def _write_events(events: list[dict[str, object]]):
        for event in events:
            csv_writer.writerow(event)

    def __formatter(event: Collection) -> list[str]:
        buffer.seek(0)
        buffer.truncate()

        if not csv_writer.fieldnames:
            csv_writer.fieldnames = list(event[0])
        if output_options.collection:
            csv_writer.writeheader()
        _write_events(event)
        return buffer.getvalue().split(DEFAULT_LINESEP)

    return __formatter
