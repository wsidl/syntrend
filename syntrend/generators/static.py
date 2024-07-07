from syntrend.generators import register, PropertyGenerator


@register
class StaticGenerator(PropertyGenerator):
    name = "static"

    def validate(self):
        assert len(self.expression) > 0, "Static Generator requires a value to be provided"

    def generate(self):
        return self.expression
