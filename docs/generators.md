# Generators

These generators are all available to use in a Configuration File. Since all properties are defined by a generator,
it is possible to provide a number of combinations of generators of the target schema.

> [!IMPORTANT]
> All Configurations require the `type` property in its configuration to know which generator it will use.

## Global Properties

These properties are globally available to all generator types.

| Property   | Default        | Description                                                                                                                                                               |
|------------|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| type       | <listed below> | Defines the generator to use. See sections below for options                                                                                                              |
| start      | none           | Provides the initial value for a property. Especially helpful for creating a series requiring a static value or a trend with a specified start value.                     |
| expression | none           | Parsable expression (using [Jinja](https://jinja.palletsprojects.com/en/3.1.x/)) used to generate expected values. More information in [Expressions Doc](expressions.md)) |

## Simple Objects

### String

Random string generator

#### Properties

| Property   | Default     | Description                                                                                                           |
|------------|-------------|-----------------------------------------------------------------------------------------------------------------------|
| type       | "string"    | Selector for this generator                                                                                           |
| chars      | [0-9a-zA-Z] | Combination of characters to be used in the random string. *Changing order or adding duplicates will impact results*. |
| min_length | 6           | Minimum length of a random string                                                                                     |
| max_length | 20          | Maximum length of a random string                                                                                     |

#### Conditions

* `chars` must have at least one character 
* Values in `chars` must be parseable by the output format selected for the dataset
* `min_length` must be equal or greater than 0
* `min_length` must be equal or less than `max_length`

#### Additional Notes
* `chars` can be a string or a list
* if `chars` is a list:
  * items can be multi-character words and `min_length`/`max_length` will apply to the number of words selected
  * items must be string values. Any other type will raise an error

#### Example

```yaml
type: string
```

```text
"d30ioen4"
```

### Integer

Generates a random integer within a range

#### Properties

| Property   | Default   | Description                 |
|------------|-----------|-----------------------------|
| type       | "integer" | Selector for this generator |
| min_offset | -500      | Minimum number (inclusive)  | 
| max_offset | 500       | Maximum number (inclusive)  |

#### Example

```yaml
type: integer
```

```text
-159
```

### Float / Double

Generates a random floating-point number within a range

#### Properties

| Property     | Default | Description                               |
|--------------|---------|-------------------------------------------|
| type         | "float" | Selector for this generator               |
| min_offset   | -500.0  | Minimum number (inclusive)                |
| max_offset   | 500.0   | Maximum number (inclusive)                | 
| num_decimals | 6       | Number of Decimal points to round a value |

#### Conditions

* `min_offset` must be less than or equal to `max_offset`

#### Additional Notes

* `num_decimals` less than 0 allows rounding to the tens, thousands, etc.

#### Example

```yaml
type: float
```

```text
291.225612
```

### Static

Generates a random integer within a range

#### Properties

| Property | Default  | Description                   |
|----------|----------|-------------------------------|
| type     | "static" | Selector for this generator   |
| value    | None     | Value to present at all times |

#### Example

```yaml
type: static
value: testing
```

```text
"testing"
```

## Expanded Types

### Hexadecimal

Generates a Hexadecimal string

> [!NOTE]
> Expanded from String Generator

#### Properties

| Property        | Default  | Description                                                                                                           |
|-----------------|----------|-----------------------------------------------------------------------------------------------------------------------|
| type            | "hex"    | Selector for this generator                                                                                           |
| chars           | [0-9a-f] | Combination of characters to be used in the random string. *Changing order or adding duplicates will impact results*. |
| min_char_length | 6        | Minimum length of a random string                                                                                     | 
| max_char_length | 20       | Maximum length of a random string                                                                                     |
| use_upper       | False    | Output value should use upper-case values for Hexadecimal string                                                      |

#### Example

```yaml
type: hex
```

```text
"39f3ad376"
```

### Date/Time

Generates a Formatted Date/Time string of the current time

#### Properties

| Property    | Default               | Description                                                                                                                                             |
|-------------|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| type        | "datetime"            | Selector for this generator                                                                                                                             |
| format      | "%Y-%m-%dT%H:%M:%S%z" | Format string (Using https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes[Python's formatting standard]) to use as output |
| time_offset | "0d"                  | Offset to apply to the generated value. Value is formatted as a sequence of numerical/suffix pairs using the regular expression `-?\d+[YmdHMS]`         |
| is_utc      | True                  | Defines if generated value is in UTC. Setting to "True" also attaches a timezone to the output                                                          |

#### Constraints

* `time_offset` values must be in a number/suffix pair with no space, `NS` where `N` is an integer and `S` is the suffix denoting the date type `N` represents.

#### Additional Notes

* Multiple sequences can be used in `time_offset`, such as `1m -15H` provides a time offset of 1 month and less 15 hours.
* If the same suffix is provided twice, the last value is kept (e.g. `1d 4H 3d` will result with offset "3 days and 4 hours")

#### Example

```yaml
type: integer
```

```text
-159
```

### Timestamp

Generates a Posix Timestamp integer of the current time

#### Properties

| Property    | Default    | Description                                                               |
|-------------|------------|---------------------------------------------------------------------------|
| type        | "datetime" | Selector for this generator                                               |
| time_offset | 0          | Numerical offset (in integer seconds) to apply to the generated timestamp |

#### Example

```yaml
type: timestamp
```

```text
1720207283
```

### Name

Generates a fake full name

#### Properties

| Property | Default | Description |
| --- | --- | --- |
| type | "name" | Selector for this generator |

#### Example

```yaml
type: name
```

```text
"Cindy Nash"
```

### First Name

Generates a fake first name

#### Properties

| Property | Default      | Description                 |
|----------|--------------|-----------------------------|
| type     | "first_name" | Selector for this generator |

#### Example


```yaml
type: first_name
```

```text
"Kathy"
```

### Last Name

Generates a fake last name

#### Properties

| Property | Default     | Description                 |
|----------|-------------|-----------------------------|
| type     | "last_name" | Selector for this generator |

#### Example

```yaml
type: last_name
```

```text
"Martinez"
```

### UUID

Generates a random UUID string

#### Properties

| Property  | Default | Description                                                         |
|-----------|--------|---------------------------------------------------------------------|
| type      | "uuid" | Selector for this generator                                         |
| use_upper | False  | Generates a UUID hex-string with upper-case characters              |
| separator | "-"    | Character separator between UUID blocks                             |
| compact   | False  | Removes separators between UUID blocks (similar to `separator: ""`) |

#### Example

```yaml
type: uuid
```

```text
"c65f9cc1-1533-4689-b373-74e2042221e1"
```

## Complex Types

### Choice

Random List Select Generator. Will generate a series of values based on the provided list of items

#### Properties

| Property | Default  | Description                     |
|----------|----------|---------------------------------|
| type     | "choice" | Selector for this generator     |
| items    | None     | List of static values to select |

#### Example

```yaml
type: choice
items:
  - red
  - green
  - blue
```

```text
"green"
```

### Union

Multi-Generator Option. Provides a mechanism for an output or nested value to be one of many different generators or same generator with different properties.

#### Properties

| Property | Default | Description                                    |
|----------|---------|------------------------------------------------|
| type     | "union" | Selector for this generator                    |
| items    | None    | List of nested generators and their properties |

#### Example

<caption>Simple Multi-type Option</caption>

```yaml
output:
  count: 5
type: union
items:
  - type: string
  - type: integer
```

```text
124
359
"qCeDy1bJeZxs"
-5
"vygu4MEPvbo3y"
```

<caption>Multiple Value Example</caption>

```yaml
output:
  count: 5
type: union
items:
  - type: string
  - type: string
    chars: abcdefg
  - type: integer
```

```text
-255
"39t4jfn3"
"fg902a"
356
"aceeabdaccefadaa"
```

### List

Generates a list of values of a specific type (using another generator type definition)

#### Properties

| Property   | Default | Description                                                                                  |
|------------|---------|----------------------------------------------------------------------------------------------|
| type       | "list"  | Selector for this generator                                                                  |
| sub_type   | -       | Generator Type properties (listed in this document) to be used for the items within the list |
| min_length | 1       | Minimum number of values to generate                                                         |
| max_length | 5       | Minimum number of values to generate                                                         |

#### Conditions

* `min_length` must be equal or greater than 0 
* `min_length` must be equal or less than `max_length`

#### Additional Notes

* a new expression value (`kwargs.index`) value is added to support expressions requiring to know the index of the list item

#### Example

<caption>Simple List Example</caption>

```yaml
type: list
sub_type:
  type: integer
```

```text
[425, 210]
```

<caption>Multiple Value Example</caption>

```yaml
output:
  count: 5
type: list
sub_type:
  type: string
  chars: abcdef
  min_length: 2
  max_length: 5
max_length: 3
```

```text
["ff", "facae", "bee"]
["ad", "fbee"]
["df", "aaeff", "fcb"]
["fd", "affe"]
["edbb", "cadfe"]
```

<caption>Nested Object Example</caption>

```yaml
type: list
sub_type:
  type: object
  properties:
    index:
      type: integer
      expression: kwargs.index
    text:
      type: string
```

```text
[{"index": 0, "text": "9tt27VDy"}, {"index": 1, "text": "aYsy5PlhnfhAV"}, {"index": 2, "text": "31ZCuqzULTHOr"}, {"index": 3, "text": "fAdrIQnL85RT9UYe"}]
```

### Object / Mapping

Generates an object/map/dictionary with nested properties with various generator types. Often used as the root object for tabular or JSON values.

#### Properties

| Property   | Default  | Description                                                 |
|------------|----------|-------------------------------------------------------------|
| type       | "object" | Selector for this generator                                 |
| properties | {}       | Map of Property Names to the generator used for this object |

#### Examples

```yaml
type: object
properties:
  value:
    type: string
```

```text
{"value": "dj430DFFUJ1"}
```
