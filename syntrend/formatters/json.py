from syntrend.config import CONFIG
from syntrend.formatters import register_formatter, Collection

ROW_FORMAT = '{row_indent}{content}{sep}'


@register_formatter('json')
def json_formatter(object_name: str):
    import json

    is_collection = CONFIG.objects[object_name].output.collection

    def __formatter(events: Collection) -> list[str]:
        buffer = ['['] if is_collection else []
        row_buffer = '  ' if is_collection else ''
        event_count = len(events)
        for idx, event in enumerate(events):
            buffer.append(
                ROW_FORMAT.format(
                    row_indent=row_buffer,
                    content=json.dumps(event['value'] if event.use_default else event),
                    sep=',' if idx < event_count - 1 and is_collection else '',
                )
            )
        if is_collection:
            buffer.append(']')
        return buffer

    return __formatter
