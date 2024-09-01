from syntrend.generators import register, PropertyGenerator


@register
class StaticGenerator(PropertyGenerator):
    name = 'static'

    def validate(self):
        if not hasattr(self.kwargs, 'value'):
            raise AttributeError("Static Generator requires a 'value' property")

    def generate(self):
        return self.kwargs.value
