from syntrend.generators import register, PropertyGenerator

from faker import Faker

fake = Faker()


@register
class NameGenerator(PropertyGenerator):
    name = "name"

    def generate(self):
        return fake.name()


@register
class FirstNameGenerator(PropertyGenerator):
    name = "first_name"

    def generate(self):
        return fake.first_name()


@register
class LastNameGenerator(PropertyGenerator):
    name = "last_name"

    def generate(self):
        return fake.last_name()
