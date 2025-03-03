from syntrend.generators import register, PropertyGenerator


@register
class IntegerGenerator(PropertyGenerator):
    type = int
    name = 'integer'
    default_config = {
        'min_offset': -500,
        'max_offset': 500,
    }
    required_modules = ['random']

    def load_kwargs(self, kwargs: dict[str, any]) -> dict[str, any]:
        kwargs['min_offset'] = int(kwargs['min_offset'])
        kwargs['max_offset'] = int(kwargs['max_offset'])
        return kwargs

    def validate(self):
        if self.kwargs.min_offset > self.kwargs.max_offset:
            raise ValueError('Min Offset must be less than or equal to Max Offset')

    def generate(self, **_):
        return self.modules.random.randint(
            self.kwargs.min_offset, self.kwargs.max_offset
        )
