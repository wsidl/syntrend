from syntrend.generators import register, PropertyGenerator


@register
class StaticGenerator(PropertyGenerator):
    name = "static"

    def validate(self):
        assert hasattr(self.kwargs, "value"), "Static Generator requires a 'value' property"

    def generate(self):
        return self.kwargs.value
