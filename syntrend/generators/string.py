from syntrend.generators import register, PropertyGenerator

from random import randint


@register
class StringGenerator(PropertyGenerator):
    name = "string"
    type = str
    default_config = {
        "chars": "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "min_length": 6,
        "max_length": 20,
    }

    def load_kwargs(self, kwargs: dict[str, any]) -> dict[str, any]:
        kwargs["min_length"] = int(kwargs["min_length"])
        kwargs["max_length"] = int(kwargs["max_length"])
        return kwargs

    def validate(self):
        assert len(self.kwargs.chars) > 0, "Cannot generate random strings without a list of characters"
        assert self.kwargs.min_length > 0, "Min Length for string generator must be greater than zero"
        assert (
            self.kwargs.min_length <= self.kwargs.max_length,
            "Min Length must be less than or equal to Max length",
        )

    def generate(self):
        return "".join([
            self.kwargs.chars[randint(0, len(self.kwargs.chars) - 1)]
            for _ in range(randint(self.kwargs.min_length, self.kwargs.max_length))
        ])


@register
class HexGenerator(StringGenerator):
    name = "hex"
    default_config = {
        "use_upper": False,
        "max_length": 20,
        "min_length": 6,
        "chars": "0123456789abcdef",
    }

    def load_kwargs(self, kwargs: dict[str, any]) -> dict[str, any]:
        kwargs["min_length"] = int(kwargs["min_length"])
        kwargs["max_length"] = int(kwargs["max_length"])
        kwargs["char_length"] = kwargs["max_length"] - kwargs["min_length"] - 1
        kwargs["use_upper"] = bool(kwargs["use_upper"])
        if kwargs["use_upper"]:
            kwargs["chars"] = kwargs["chars"].upper()
        return kwargs

    def validate(self):
        assert self.kwargs.min_length <= self.kwargs.max_length, "Min Length must be less than or equal to Max Length"
        assert self.kwargs.char_length >= 0, "Cannot generate string from an empty list"

    def generate(self):
        return "".join([
            self.kwargs.chars[randint(0, self.kwargs.char_length)]
            for _ in range(randint(self.kwargs.min_length, self.kwargs.max_length))
        ])
