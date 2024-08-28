from syntrend.formatters import register_formatter, Event, Collection
from syntrend.config import CONFIG

from functools import cache

cell_format = "{l_buffer}{value}{r_buffer}"
row_format = " {cols} "


@register_formatter('table')
def table_formatter(object_name: str):
    output_options = CONFIG.objects[object_name].output
    col_sep = output_options.kwargs.get("column_separator", " ")
    if col_sep != " ":
        col_sep = f" {col_sep} "
    column_widths: dict[str, int] = {}

    @cache
    def table_width():
        return sum(column_widths.values()) + (len(col_sep) * (len(column_widths) - 1)) + 2
        # Table Width = (total of max widths) + ( (width of separator) * (# cols - 1) ) + 2 extra spaces at start/end

    def _write_rows(events: Collection, row_sep: str) -> list[str]:
        buffer = []
        for event in events:
            row = []
            for key, value in event.items():
                l_adjust = isinstance(value, (str, ))
                cell_buffer = " " * (column_widths[key] - len(str(event[key])))
                row.append(
                    cell_format.format(
                        l_buffer="" if l_adjust else cell_buffer,
                        r_buffer="" if not l_adjust else cell_buffer,
                        value=value,
                    )
                )
            buffer.append(row_format.format(cols=col_sep.join(row)))
            if row_sep:
                buffer.append(row_sep * table_width())
        return buffer

    def __formatter(events: Collection) -> list[str]:
        buffer = []
        column_widths.clear()
        for event in events:
            widths: dict[str, int] = {}
            for key, value in event.items():
                cell_width = len(str(value))
                column_widths[key] = max(len(key), column_widths.get(key, 0), cell_width)
                widths[key] = cell_width
        if output_options.collection:
            buffer += _write_rows(
                events=Collection(Event(**{key: key for key in column_widths})),
                row_sep=output_options.kwargs.get("header_separator", "="),
            )
        buffer += _write_rows(
            events=events,
            row_sep=output_options.kwargs.get("row_separator", ""),
        )
        return buffer

    return __formatter
