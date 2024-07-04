# Generator Configurations

These generators are all available to use in a Configuration File. Since all properties are defined by a generator,
it is possible to provide a number of combinations of generators of the target schema.

> All Configurations require the `type` or `property_type` property in its configuration to know which generator it will use.

## Simple Objects

### String

> Random string generator

| Config Property | default                                | Description                                                                                                           |
|-----------------|----------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| type            | "string"                               | Defines this generator will be used                                                                                   |
| chars           | "abcdefghijklmnopqrstuvwxyz0123456789" | Combination of characters to be used in the random string. *Changing order or adding duplicates will impact results*. |
| min_char_length | 6                                      | Minimum length of a random string                                                                                     |
| max_char_length | 20                                     | Maximum length of a random string                                                                                     |

