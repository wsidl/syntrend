from random import randint
from syntrend.generators import register, PropertyGenerator


@register
class ChoiceGenerator(PropertyGenerator):
    """Generator to randomly provide one of many Generator Types for a value

    Args:
        items (list): List of static values to select from

    Example:
        Selectively choose a generator randomly or through the use of an expression::

            type: choice
            items:
                - a random string
                - 155
                - [a, list, of, 166, 215, numbers]
    """

    name = 'choice'

    def validate(self):
        assert len(self.items) > 0, 'Cannot generate items from an empty list'

    def generate(self, **_):
        return self.items[randint(0, len(self.items) - 1)]
