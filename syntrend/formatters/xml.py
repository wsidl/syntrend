from syntrend.config import CONFIG, model
from syntrend.formatters import register_formatter, Collection


@register_formatter('xml')
def xml_formatter(object_name: str):
    from xml.etree import ElementTree

    object_root = CONFIG.objects[object_name]
    is_collection = object_root.output.collection

    def handle_attribute(name: str, value: any, properties: model.PropertyDefinition):
        if properties.type == 'list':
            raise TypeError(
                'XML Attributes cannot have multiples or be lists',
                {
                    'Property Name': name,
                    'Property Definition': str(properties),
                },
            )
        if type(value) in {dict, list}:
            raise TypeError(
                'XML Attributes must contain simple values',
                {
                    'Property Name': name,
                    'Property Definition': str(properties),
                },
            )
        return value

    def handle_sub_element(
        parent: ElementTree.Element,
        name: str,
        value: any,
        properties: model.PropertyDefinition,
    ):
        if type(value) is list:
            for item in value:
                handle_sub_element(
                    parent,
                    name,
                    item,
                    model.PropertyDefinition(**properties.kwargs.get('sub_type')),
                )
            return

        if type(value) is dict:
            parent.append(generate_xml(name, properties, value))
            return

        if parent.text:
            parent.text += value
        else:
            parent.text = value

    def generate_xml(
        name: str, object_properties: model.PropertyDefinition, event: dict
    ):
        tag_name = object_properties.kwargs.get('xml_tag', name)
        element = ElementTree.Element(tag_name)

        for prop_name, prop in object_properties.properties.items():
            tag = prop.kwargs.get('xml_tag', prop_name)

            if prop.kwargs.get('xml_attr', False):
                element.attrib[tag] = handle_attribute(
                    prop_name, event[prop_name], prop
                )
                continue

            handle_sub_element(element, prop_name, event[prop_name], prop)
        return element

    def __formatter(events: Collection) -> list[str]:
        root = None
        if is_collection:
            root = ElementTree.Element(object_root.output.get('xml_tag', 'data'))

        for event in events:
            if is_collection:
                root.append(generate_xml(object_root.name, object_root, event))
            else:
                root = generate_xml(object_root.name, object_root, event)

        ElementTree.indent(root)
        buffer = (
            ElementTree.tostring(root, encoding='utf-8', xml_declaration=True)
            .decode('utf-8')
            .split('\n')
        )
        return buffer

    return __formatter
