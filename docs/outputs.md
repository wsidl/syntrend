# Output Formats

Data we use come in a wide range of formats and structures. Syntrend is intended to support all teams to simulate
all forms of data. To support this functionality, Syntrend will output it's content in a wide range of formats
for applications to consume.

## Define the Output Format

There are two ways to define how an object will be formatted, at the Project level or for each Object.

> [!NOTE]
> Details on the Output Formats are found in the [Output Config](project_file.md#output-config) documentation

For defining a common format for all objects, you can define the configurations at the root of the project. Any updates at the object-level takes precedence and will be applied

```yaml
output:
  format: csv
  directory: output_csv
  filename_Format: "{name}.{format}"
  collection: true
objects:
  old_data:
    output:
      count: 10
    type: object
    properties:
      field_1:
        type: string
  new_data:
    output:
      format: json
      collection: false
    type: string
```

This project will output a CSV file (named "my_data.csv") containing a single "field_1" column and 10 records and a JSON file (named "new_data.json") containing a single string.

```text
my_data.csv:

"field_1"
"eB43K1r9T"
"GvuKBo5zqRyS4"
"xkM3uP0JatmS"
"Xx49Albq4Q1hfnb"
... (+6 records)


new_data.json:

"cvpXrZaDWH0nnZ"
```

## Events vs Collections

Data can be considered in many forms, but more general ideas for data can be considered as a Static Dataset (collection) or individual updates (events). Each have their use cases and Syntrend intends to support both.

**Collections** support relational datasets where a large collection of entries are gathered in one place. Common ideas for this is a Data Table or a collection of entries. These are useful when populating a database or creating a file-based source reference.

**Events** are smaller data updates to simulate human or machine activity. Examples include API requests, IoT/event-driven messaging, human-driven activity.

To set a dataset as a **Collection**, apply the `collection` [Output Config](project_file.md#output-config) value to `true` (default is false).

```yaml
output:
  collection: true
```

## Real-Time Simulations

> [!TIP]
> This topic involves the [Output Module](project_file.md#output-config)'s `time_field` property.

Specific for **Events** (although some use cases of **Collections** benefitting from this) is the need to simulate when data is generated according to a specific timestamp. This is highly relevant to datasets involving event-driven messaging such as IoT sensors, load testing, or logic testing involving time-sensitive operations.

Syntrend supports simulating these event updates by defining a field within an object that determines the time interval to generate events using the [Output Module](project_file.md#output-config)'s `time_field` property.

For example, creating a simple project as follows would generate a list of values that would be written to the output console immediately.

```yaml
output:
  count: 5
type: object
properties:
  timestamp:
    type: timestamp
    start: 1735689600
    expression: random(0, 5) + this(1).timestamp
  name:
    type: choice
    items:
      - John
      - Jane
  sensor:
    type: integer
```

![Output Sequence of events to console with no time simulations](assets/output_seq_no_time_sim.gif)

By introducing the `time_field` property to the [Output Config](project_file.md#output-config) block and set it to the `timestamp` field, we now have defined the object to simulate event updates based on the increments presented by that field.

```yaml
output:
  count: 5
  time_field: timestamp
type: object
properties:
   ...
```

![Value Updates with Time simulation](assets/output_seq_with_time_sim.gif)

Writing **Events** to a file would not accurately support the reactivity of these events. Instead, we may want to pipe these outputs to another process which can do something with these events.

```shell
syntrend generate event_stream.yaml | kafka-shell-producer.sh --broker-list localhost:9092 --topic test
```

> [!IMPORTANT]
> Please read the next section if dealing with multiple object outputs.

## Output Targets

### File

> [!IMPORTANT]
> Set the object's [Output Config](project_file.md#output-config) `directory` path to a known path on the file system.

By providing an output directory for an object, you immediately define the object is to be written to a file.

Some things to know when handling file outputs:

1. The `directory` Output Config is a directory where a collection of files will be written. If it doesn't exist, Syntrend will attempt to create it.
2. `filename_format` is a template string to define how output files will be written. By default, it uses `{name}_{id}.{format}`. For more information about `filename_format`, please see the [Filename Format Template](project_file.md#filename-format-template).

### Console

> [!IMPORTANT]
> By default, all output is written to the interactive console (stdout). To change this behaviour, the [Output Module](project_file.md#output-config)'s `directory` value must be set to a valid directory path. Using "." will use the current working directory.

When generating outputs for data generation, where they are written highly depends on their use case. Following on the [Events vs Collections](#events-vs-collections) discussion, knowing when to use which is important.

For most use cases, **Collections** would benefit from writing the output to a file to be consumed. Think of [SQL](#sql) or [CSV](#csv) datasets that would be consumed by a data processor.

The inverse of this are **Events** which typically need to simulate real-time activity (see the above section [Real-Time Simulations](#real-time-simulations)).

#### Additional Notes

1. By writing to the console, only the content of the data will be written.
2. **Collections** are written to console first with **Events** written after.
2. Both **Collections** and **Event** output types can have custom output formats to allow some differentiation. See [Console Output Formats](project_file.md#console-output-formats). 

## Exchange Formats

### JSON

> [!NOTE]
> This is the default format type
> 
> `format: json`

Formats any data as a JSON value. If the data is a primary type (string, integer, boolean, etc), it is parsed as a single value with appropriate enclosures (strings with double-quotes while numbers have no enclosures).

String example:

```yaml
output:
  format: json
type: string
```

```json
"ri39gv23i9g"
```

While a more complex structure can look like:

```yaml
output:
  format: json
type: object
properties:
  field_1:
    type: string
  field_2:
    type: integer
```

```json
{
  "field_1": "39h094g1l",
  "field_2": -31
}
```

And using a collection looks like this:

```yaml
output:
  format: json
  collection: true
  count: 2
type: integer
```

```json
[
  -7,
  121
]
```

### CSV

> [!NOTE]
> `format: csv`

Commonly used with **Collections** to create a structured table with `object` object-types where fields can be defined.

> [!TIP]
> If not using `object` and a single value type is required, a field named "value" is assigned.

Single Value example:

```yaml
outputs:
  format: csv
  collection: true
type: string
```

```csv
"value"
"0FrPmtVJRXcvsi9NRZG"
```

Creating a Tabular Dataset:

```yaml
outputs:
  format: csv
  collection: true
  count: 3
type: object
properties:
  id:
    type: integer
    expression: interval
  field_1:
    type: string
  field_2:
    type: integer
```

```text
"id","field_1","field_2"
0,"q8tVoM9TKf",-160
1,"LmuqKKWLSJwiR11i8g7",462
2,"agpofNhQ1GovrD",85
```

### XML

> [!NOTE]
> `format: xml`

XML is a complex format compared to many of these other formats. XML Elements (tags) behave like JSON/YAML Objects **AND** Ordered Lists, so to find ways to define it can be tricky.

How Syntrend supports this is to look at each element as an object. The properties of this object can either be an attribute of the element or a child element.

#### Properties

| Property     | Where                                                      | Default       | Description                                                                 |
|--------------|------------------------------------------------------------|---------------|-----------------------------------------------------------------------------|
| **xml_tag**  | `output`                                                   | object name   | The XML Tag name used to encapsulate all elements when `collection: true`   |
| **xml_tag**  | [Property Definition](project_file.md#property-definition) | property name | Alternative XML Tag used for the attribute/child element                    |
| **xml_attr** | [Property Definition](project_file.md#property-definition) | "false"       | Flag to identify the property as an XML Attribute                           |

#### Examples

##### Simple XML Example

```yaml
output:
  format: xml
type: object
xml_tag: root
properties:
  attr:
    type: string
    xml_attr: true
  child:
    type: object
    properties:
      attr:
        type: string
        xml_attr: true
      content:
        type: string
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<root attr="mmiOBE8Uf2">
  <child attr="uaTQex3q5HKnVjywgtAG">0OzxfgIQJ</child>
</root>
```

##### Hybrid Statis/Dynamic XML Generation
Of course, XML can support many nested elements (HTML is a great example of many types of nested objects under one parent). Sometimes you need to clearly define the element, and sometimes you want to have a random number of those elements provided.

Syntrend can support this use case through the use of the [List Generator](generators.md#list) as an object type. Since XML Elements are naturally Objects and Lists, any List object within a Syntrend project will have it's child objects collapse to the parent in the order where the List object was situated.

```yaml
objects:
  html:
    output:
      format: xml
    type: object
    properties:
      head:
        type: object
        properties:
          title:
            type: object
            properties:
              string:
                type: name
      body:
        type: object
        properties:
          header:
            type: object
            xml_tag: h1
            properties:
              string:
                type: string
                expression: html().head.title.string
          paragraph1:
            type: object
            xml_tag: p
            properties:
              class:
                type: string
                xml_attr: true
              string:
                type: string
          new_list:
            type: object
            xml_tag: ul
            properties:
              first_item:
                type: object
                xml_tag: li
                properties:
                  string:
                    type: static
                    value: First Item
              list_items:
                type: list
                min_length: 2
                max_length: 4
                sub_type:
                  type: object
                  xml_tag: li
                  properties:
                    string:
                      type: string
              last_item:
                type: object
                xml_tag: li
                properties:
                  string:
                    type: static
                    value: Last Item
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<html>
  <head>
    <title>Craig Barnes</title>
  </head>
  <body>
    <h1>Craig Barnes</h1>
    <p class="GKbrm8gDlIqtz">HgL4gwHzxIEqMaB</p>
    <ul>
      <li>First Item</li>
      <li>wdQgaB2DcTcu9r8pZA9</li>
      <li>JYvuPWXdDATDbweIa</li>
      <li>i1qerN2YCmXXQv</li>
      <li>Last Item</li>
    </ul>
  </body>
</html>
```

##### Collections

Since XML is a document, a collection of documents would be separated into multiple files or entities. So for Syntrend to support collections of XML documents, it needs to enclose the whole collection in another XML element.

An example of this is a Geographic Markup Language (GML) Feature Collection. If creating a single Feature element, we can define a project as follows.

<caption>Single GML Feature Element</caption>

```yaml
Feature:
  output:
    format: xml
  type: object
  properties:
    fid:
      type: integer
      expression: interval
      xml_attr: true
    Description:
      type: string
      xml_attr: true
    Point:
      type: object
      properties:
        srsName:
          type: static
          value: urn:ogc:def:crs:EPSG::4326
          xml_attr: true
        srsDimension:
          type: static
          value: 2
          xml_attr: true
        pos:
          type: object
          properties:
            lat:
              type: float
              min_offset: -90
              max_offset: 90
            lon:
              type: float
              min_offset: -180
              max_offset: 180
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<Feature fid="0" Description="9QARr9V3gMPC">
  <Point srsName="urn:ogc:def:crs:EPSG::4326" srsDimension="2">
    <pos>
      -24.076383
      19.308395
    </pos>
  </Point>
</Feature>
```

> [!NOTE]
> Notice how multiple child values used in the `pos` object
> (`lat`, `space`, and `lon`) is concatenated in the 
> final result (as `-24.076383 19.308395`)

Adding `collection: true` to the [Output Config](project_file.md#output-config) of the object along with the XML Tag to be used (`xml_tag`) will encapsulate all generated elements by that tag.

<caption>Collection of Features in a FeatureCollection element</caption>

```yaml
Feature:
  output:
    format: xml
    collection: true
    xml_tag: FeatureCollection
    count: 3
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<FeatureCollection>
  <Feature fid="0" Description="rLWWnWr">
    <Point srsName="urn:ogc:def:crs:EPSG::4326" srsDimension="2">
      <pos>
        -38.472894
        -64.3371
      </pos>
    </Point>
  </Feature>
  <Feature fid="1" Description="pLnYqyA3ObdA">
    <Point srsName="urn:ogc:def:crs:EPSG::4326" srsDimension="2">
      <pos>
        -64.808272
        -107.701463
      </pos>
    </Point>
  </Feature>
  <Feature fid="2" Description="n3Fyu349M5HeTMyX">
    <Point srsName="urn:ogc:def:crs:EPSG::4326" srsDimension="2">
      <pos>
        -71.014564
        67.249924
      </pos>
    </Point>
  </Feature>
</FeatureCollection>
```

### SQL

> [!NOTE]
> `format: sql`

For creating a Generic SQL output file that can be used with database processors to populate a database.

#### Examples

For a process that creates a new schema like the following:

```sql
create table my_data (id integer, field_1 varchar(20), field_2 integer); 
```

Creating a dataset to fulfill this table would look like this project:

```yaml
outputs:
  format: sql
  collection: true
  count: 3
objects:
  my_data:
    type: object
    properties:
      id:
        type: integer
        expression: interval
      field_1:
        type: string
      field_2:
        type: integer
```

to output

```sql
insert into my_data (id, field_1, field_2) values (0, "CSCjEaamUmNthhNYu", 358);
insert into my_data (id, field_1, field_2) values (1, "2FXXIJfpg3V02WDRg", -243);
insert into my_data (id, field_1, field_2) values (2, "wHd6hkT2NlyjdJE5", 314);
```

## Display Formats

This is typically useful for human-readable reports.

### ASCII Table

> ![!TIP]
> `format: table`

This creates a spaced dataset using various ascii characters to define a visual table border structure.

If using the above example in [SQL](#sql) and set `output.format: table`, you would get a table output suitable to read in the console.

```text
 id field_1            field_2 
===============================
  0 Pgu2CLzuTE7ElLeAJe     387 
  1 zbYcjLn8w              283 
  2 oHjbCj1q6WP            -16 
```

> [!TIP]
> For Customizations to the table formatting, adjust the object's [Output Properties specific for `format: table`](project_file.md#conditional-properties)
> 
> e.g. setting `header_separator: "~"` would produce this output
> 
> ```text
>  id field_1             field_2 
> ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
>   0 GGZN8CYJt1M06WjpQJr    -141 
>   1 Qk6kEg                   63 
>   2 UViL1NVx               -219 
> ```

## Custom Output Targets and Formats

There may be formats or output targets Syntrend would not be able to support generically without including extensive driver libraries and adding external dependencies. For this reason, Syntrend supports the ability to create Custom Formatters.

Customer Formatters would be a Python script containing a function that registers itself into the Syntrend ecosystem. If the script is project-specific, save the script in a dedicated location and set the project's `output.formatter_dir` to this directory.

This also applies to dedicated output targets. It would be possible to have a formatter write data directly to a target, bypassing the output writer complete and instead use the output writer to produce a debug log. Use case for this is to write directly to a database or make API requests.

### Base Example of Custom Writer

The following example would produce a bare minimum implementation of a custom formatter.

File `formatter/minimum.py`:

```python
from syntrend.formatters import register_formatter


@register_formatter('min')
def min_formatter(object_name: str):
    def my_writer(events):
        lines = []
        for event in events:
            # Events are dictionaries of each object.
            # This is where you would 
            # write to an external target if desired
            lines.append(
                f'{object_name}: '
                f'id={event["id"]}, '
                f'f1={event["field_1"]}, '
                f'f2={event["field_2"]}'
            )
        return lines

    return my_writer
```

File `project.yaml`

```yaml
output:
  format: min
  formatter_dir: formatter
objects:
  my_data:
    type: object
    properties:
      id:
        type: integer
        expression: interval
      field_1:
        type: string
      field_2:
        type: integer
```

Running this project would result in the following.

```text
# syntrend generate project.yaml
my_data: id=0, f1=4NLwTO3x8J3uj9k5eq, f2=245
my_data: id=1, f1=zfU2qFLrcUAc4hsdajx, f2=-251
my_data: id=2, f1=bAPeCivCOnjbCuCtr, f2=172
```
