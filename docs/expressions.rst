Property Expressions
====================

.. toctree::
    :maxdepth: 2

Building out generators to express specific trends and behaviours within a dataset, expressions are necessary to provide some logic to build that result.

.. seealso::

    Information presented here is in relation to :attr:`PropertyDefinition.expression`

Summary
-------

All Expressions are built using the `Jinja2 <https://jinja2.palletsprojects.com>`__ templating engine. Please read more information on their page on how to build expressions.

Relevant to this project is the inclusion of additional filters and variable references.

Variables
---------

Provided variables to all expressions include:

**new**::
    a randomly-generated value based on the generator type before applying the expression

**interval**::
    a zero-indexed (starts at 0) counter of the object instance being generated within a sequence

**(object name)**::
    The named-reference of the Object to refer. More information in `Object References <#Object_References>`_

**pi**::
    Mathematical `pi`, :math:pi

Object References
`````````````````

Objects are defined a number of different ways and can also in sequences. They are also critical in expressions to define how a sequence will progress or change over time. For this reason, **Object References** are defined as:

* The name of the reference/variable is the name of the object in the `Project File`:

    For example, for the following project:

    .. code-block:: yaml

        objects:
            obj1:
                type: integer
            obj2:
                type: integer

    An expression from `obj2` would call `obj1` as a variable: `expression: "obj1() + 1"`

* The reference variable is a method accepting an index value. The default is the current value while any positive number is the previous instance in the sequence.

    For example, `expression: "obj(4)"` will refer to the object reference the 4th previous "obj" instance.

* Mapping/Object-type references will access nested properties as attributes.

    For example, an object named "backfill" with a generated a JSON object below:

    .. code-block:: json

        {
            "timestamp": 1958293914,
            "type": "sensor",
            "part": {
                "make": "maker one",
                "model": "mddr_3144",
                "created": 1722895919
            },
            "value": {
                "temp": 51.318,
                "radius": 2.14872,
                "accuracy": 81.3901
            }
        }

    Can access it's properties to format a new string: `expression: 'backfill().part.make + "|" + backfill().part.model + "=" + backfill().value.accuracy'` to produce a string value "maker one|mddr_3144=81.3901"

Filters
-------

Filters in Jinja2 expressions are simply functions where a value can be piped into it as it's first argument. Jinja2 already provides a number of filters included

.. seealso::

    Jinja2 List of Built-in Filters: `<https://jinja.palletsprojects.com/en/3.1.x/templates/#list-of-builtin-filters>`__

e.g. `interval * 10 / pi | sin * 5 + 2` will pipe the result of the arithmetic as the value into sin to then apply more calculations.



Date Filters
````````````

**datetime**::
    Produce a Python `:obj:datetime.datetime` object: `"datetime(year=2024, month=1, day=1).totimestamp()"` will generate a timestamp of January 1, 2024.

**date**::
    Produce a Python `:obj:datetime.date` object: `date(2024, 1, 1)`

**time**::
    Produce a Python `:obj:datetime.time` object: `time(15, 0)`

**to_datetime**::
    Translate a formatted object into a Python `:obj:datetime.datetime` object. Possible inputs include formatted strings or timestamps: `"2024-01-01T15:23+02:00" | to_datetime` or `"5:00 PM, Jan 1, 2024" | to_datetime("%H:%M %p, %b %d, %Y")`

**to_timestamp**::
    Takes an existing datetime object and converts it into an integer timestamp: `datetime(2024, 1, 1) | to_timestamp`.

    Convenience function to replace `datetime(2024, 1, 1).totimestamp()`

**timedelta**::
    Produce a Python `:obj;datetime.timedelta` object (which results in an integer): `"obj().iso_time | to_datetime - timedelta(days=-1)`

Math Filters
````````````

**sin**::
    Produces the Sine of a value given in Radians (see example in the note under `Filters <#Filters>`__.

**cos**::
    Produces the Cosine of a value given in Radians.

**tan**::
    Produces the Tangent of a value given in Radians.

**degress**::
    Translates a number from Radians to Degrees.

**radians**::
    Translates a number from Degrees to Radians.

**random**::
    Generates a random, floating-point number from 0 to 1 (inclusive)