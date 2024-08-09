from syntrend.generators import register, PropertyGenerator


@register
class UUIDGenerator(PropertyGenerator):
    type = str
    name = "uuid"
    default_config = {
        "use_upper": False,
        "compact": False,
    }
    required_modules = ["uuid"]

    def load_kwargs(self, kwargs: dict[str, any]) -> dict[str, any]:
        kwargs["use_upper"] = bool(kwargs["use_upper"])
        kwargs["compact"] = bool(kwargs["compact"])
        return kwargs

    def generate(self):
        uuid_val = self.modules.uuid.uuid4()
        if self.kwargs.compact:
            uuid_val = uuid_val.hex
        uuid_val = str(uuid_val)
        if self.kwargs.use_upper:
            uuid_val = str(uuid_val).upper()
        return uuid_val
