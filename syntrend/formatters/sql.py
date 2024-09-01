from syntrend.config import CONFIG
from syntrend.formatters import register_formatter, Collection

SQL_INSERT_FORMAT = "insert into {table} ({columns}) values ({values})"


@register_formatter('sql')
def sql_formatter(object_name: str):
    _ = CONFIG.objects[object_name].output  # To satisfy testing and lint requirements

    def __format_value(value):
        if isinstance(value, str):
            return f'"{str(value)}"'
        return str(value)

    def __format_event(event: dict) -> str:
        return SQL_INSERT_FORMAT.format(
            table=object_name,
            columns=", ".join(list(event)),
            values=", ".join(map(__format_value, event.values())),
        )

    def __formatter(events: Collection) -> list[str]:
        return list(map(__format_event, [ev if isinstance(ev, dict) else {"value": ev} for ev in events]))

    return __formatter
