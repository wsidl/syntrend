from syntrend.generators import register, PropertyGenerator


@register
class FloatGenerator(PropertyGenerator):
    type = float
    name = "float"
    default_config = {
        "min_offset": -500.,
        "max_offset": 500.,
        "num_decimals": 6,
    }
    required_modules = ["random"]

    def load_kwargs(self, kwargs: dict[str, any]) -> dict[str, any]:
        kwargs["min_offset"] = float(kwargs["min_offset"])
        kwargs["max_offset"] = float(kwargs["max_offset"])
        kwargs["num_decimals"] = int(kwargs["num_decimals"])
        kwargs["range"] = kwargs["max_offset"] - kwargs["min_offset"]
        return kwargs

    def validate(self):
        assert (
            self.kwargs.min_offset <= self.kwargs.max_offset,
            "Min Offset must be less than or equal to Max Offset",
        )

    def generate(self):
        return round(
            self.modules.random.random() * self.kwargs.range + self.kwargs.min_offset,
            self.kwargs.num_decimals,
        )
