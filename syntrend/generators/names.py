from syntrend.generators import register, PropertyGenerator

from faker import Faker

fake = Faker()


@register
class NameGenerator(PropertyGenerator):
    type = str
    name = 'name'

    def generate(self, **_):
        return fake.name()


@register
class FirstNameGenerator(PropertyGenerator):
    type = str
    name = 'first_name'

    def generate(self, **_):
        return fake.first_name()


@register
class LastNameGenerator(PropertyGenerator):
    type = str
    name = 'last_name'

    def generate(self, **_):
        return fake.last_name()
