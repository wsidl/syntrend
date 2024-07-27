from syntrend.generators import register, PropertyGenerator, get_generator

from random import randint


@register
class UnionGenerator(PropertyGenerator):
    name = "union"

    def load_items(self, items: list[any]) -> list[any]:
        _gens = []
        for item in items:
            _gens.append(get_generator(item, self.root_manager))
        return _gens

    def generate(self) -> any:
        return self.items[randint(0, len(self.items) - 1)].compile()


@register
class ObjectGenerator(PropertyGenerator):
    name = "object"

    def load_properties(self, properties: dict[str, any]) -> dict[str, PropertyGenerator]:
        return {
            key: get_generator(properties[key], self.root_manager)
            for key in properties
        }

    def generate(self):
        for key in self.properties:
            self.properties[key].compile()
        return {
            key: self.properties[key].compile()
            for key in self.properties
        }
