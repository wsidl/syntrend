from syntrend.generators import register, PropertyGenerator, get_generator

from random import randint


@register
class UnionGenerator(PropertyGenerator):
    name = "union"

    def load_items(self, items: list[any]) -> list[any]:
        _gens = []
        for item in items:
            _gens.append(get_generator(item))
        return _gens

    def generate(self) -> list[any]:
        return self.items[randint(0, len(self.items) - 1)].generate()


@register
class ObjectGenerator(PropertyGenerator):
    name = "object"

    def load_properties(self, properties: dict[str, any]) -> dict[str, PropertyGenerator]:
        return {
            key: get_generator(properties[key])
            for key in properties
        }

    def generate(self):
        return {
            key: self.properties[key].generate()
            for key in self.properties
        }
