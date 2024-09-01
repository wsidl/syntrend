from random import randint
from syntrend.generators import register, PropertyGenerator


@register
class ChoiceGenerator(PropertyGenerator):
    name = 'choice'

    def validate(self):
        assert len(self.items) > 0, 'Cannot generate items from an empty list'

    def generate(self):
        return self.items[randint(0, len(self.items) - 1)]
