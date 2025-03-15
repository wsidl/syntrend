from syntrend.generators import register, PropertyGenerator

from random import randint


@register
class StringGenerator(PropertyGenerator):
    """String Generator

    Keyword Args:
        min_length (:obj:`int`): Minimum length for a random string. Default is `6`
        max_length (:obj:`int`): Maximum length for a random string. Default is `20`
        chars (:obj:`list[str] | str`)::
            List of characters to be used for random string generation. **Changing order or adding
            duplicates will impact results**. Default is the sequence: "[0-9a-zA-Z]".

    Raises:
        ValueError::
            - Length of :attr:`chars` is not greater than one
            - :attr:`min_length` is less than 1
            - :attr:`max_length` is less than :attr:`min_length`

    Notes:
        - Values in :attr:`chars` must be parseable as a string object
        - :attr:`chars` can be a list
            - items can be individual characters or multi-character words. Something like the following can create a sequence like `"is bigthisis biglist"`

                type: string
                min_length: 3
                max_length: 6
                chars:
                    - this
                    - list
                    - is big

    """

    name = 'string'
    type = str
    default_config = {
        'chars': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'min_length': 6,
        'max_length': 20,
    }

    def load_kwargs(self, kwargs: dict[str, any]) -> dict[str, any]:
        kwargs['min_length'] = int(kwargs['min_length'])
        kwargs['max_length'] = int(kwargs['max_length'])
        return kwargs

    def validate(self):
        if len(self.kwargs.chars) <= 0:
            raise ValueError(
                'Cannot generate random strings without a list of characters'
            )
        if self.kwargs.min_length <= 0:
            raise ValueError(
                'Min Length for string generator must be greater than zero'
            )
        if self.kwargs.min_length > self.kwargs.max_length:
            raise ValueError('Min Length must be less than or equal to Max length')

    def generate(self, **_):
        return ''.join(
            [
                self.kwargs.chars[randint(0, len(self.kwargs.chars) - 1)]
                for _ in range(randint(self.kwargs.min_length, self.kwargs.max_length))
            ]
        )


@register
class HexGenerator(StringGenerator):
    name = 'hex'
    default_config = {
        'use_upper': False,
        'max_length': 20,
        'min_length': 6,
        'chars': '0123456789abcdef',
    }

    def load_kwargs(self, kwargs: dict[str, any]) -> dict[str, any]:
        kwargs['min_length'] = int(kwargs['min_length'])
        kwargs['max_length'] = int(kwargs['max_length'])
        kwargs['char_length'] = kwargs['max_length'] - kwargs['min_length'] - 1
        kwargs['use_upper'] = bool(kwargs['use_upper'])
        if kwargs['use_upper']:
            kwargs['chars'] = kwargs['chars'].upper()
        return kwargs

    def validate(self):
        assert self.kwargs.min_length <= self.kwargs.max_length, (
            'Min Length must be less than or equal to Max Length'
        )
        assert self.kwargs.char_length >= 0, 'Cannot generate string from an empty list'

    def generate(self, **_):
        return ''.join(
            [
                self.kwargs.chars[randint(0, self.kwargs.char_length)]
                for _ in range(randint(self.kwargs.min_length, self.kwargs.max_length))
            ]
        )
