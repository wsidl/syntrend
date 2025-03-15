from syntrend.config import CONFIG, model
from syntrend.formatters import register_formatter, Collection


@register_formatter('xml')
def xml_formatter(object_name: str):
    from xml.dom import minidom

    dom_impl = minidom.getDOMImplementation()
    object_root = CONFIG.objects[object_name]
    is_collection = object_root.output.collection
    doc = dom_impl.createDocument(None, None, None)

    def handle_attribute(name: str, value: any, properties: model.PropertyDefinition):
        if properties.type in {'object', 'list'}:
            raise TypeError(
                'XML Attributes cannot have multiples or be lists',
                {
                    'Property Name': name,
                    'Property Definition': str(properties),
                },
            )
        if type(value) in {dict, list}:
            raise ValueError(
                'XML Attributes must contain simple values',
                {
                    'Property Name': name,
                    'Property Definition': str(properties),
                },
            )
        str_value = str(value)
        return str_value

    def handle_sub_element(
        parent: minidom.Element,
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
            new_node = generate_xml(name, properties, value)
        else:
            str_value = str(value)
            new_node = doc.createTextNode(str_value)
        parent.appendChild(new_node)

    def generate_xml(
        name: str, object_properties: model.PropertyDefinition, event: dict
    ):
        tag_name = object_properties.kwargs.get('xml_tag', name)
        element = doc.createElement(tag_name)

        for prop_name, prop in object_properties.properties.items():
            tag = prop.kwargs.get('xml_tag', prop_name)

            if prop.kwargs.get('xml_attr', False):
                element.attributes[tag] = handle_attribute(
                    prop_name, event[prop_name], prop
                )
                continue

            handle_sub_element(element, prop_name, event[prop_name], prop)
        return element

    def __formatter(events: Collection) -> list[str]:
        doc.childNodes.clear()
        root = doc
        if is_collection:
            root = doc.createElement(object_root.output.kwargs.get('xml_tag', 'data'))
            doc.appendChild(root)

        for event in events:
            root.appendChild(generate_xml(object_root.name, object_root, event))

        buffer = (
            doc.toprettyxml(indent='  ', encoding='utf-8')
            .decode('utf-8')
            .split('\n')[:-1]
        )
        return buffer

    return __formatter
