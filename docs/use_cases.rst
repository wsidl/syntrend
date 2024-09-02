Common Use Cases for Synthetic Trend Data Generation
====================================================

The "SynTrend" utility is intended to be highly configurable to support a range of use cases.
Some use cases are intuitive to support while others require some creativity to provide the
intended outcome.

Simple Use Cases
----------------

These use cases focus on situations you would be able to support the functionality with little complexity
based on the available project documentation.

Single-Value Generation
```````````````````````

Using a simple project configuration, you can create a single value dataset of your choice. This allows
the project file to only implement the value type, its value configuration, and potentially an output target.

String Value
^^^^^^^^^^^^

String-Type Value to generate random string between 8 and 10 characters long. This uses the `type` property
to define the generator to use and any following properties are provided along with it.

In this example, `type: string` is defined for String generation with `min_length` and `max_length` properties
to set how long the random string will be.

.. literalinclude:: ../tests/assets/uc_single_value_string.yaml
   :language: yaml
   :emphasize-lines: 1

.. code-block:: shell-session

   $ syntrend generate single_value_string.yaml
   "ezS3H0JdIV"

Integer Value
^^^^^^^^^^^^^

Implementing an Integer-Type Value (to generate any number between 5 and 10) is simple by providing
the `type: integer` property.

.. literalinclude:: ../tests/assets/uc_single_value_integer.yaml
   :language: yaml

.. code-block:: shell-session

   $ syntrend generate single_value_integer.yaml
   6

Random Value Selection
^^^^^^^^^^^^^^^^^^^^^^

It's also possible to provide a list of pre-defined values using the `type: choice` generator and
the list of values it would use.

.. literalinclude:: ../tests/assets/uc_random_choice.yaml
   :language: yaml

.. code-block:: shell-session

   $ syntrend generate random_color.yaml
   "blue"

Object Value
^^^^^^^^^^^^

Object-Type Value with properties containing their own definitions

.. literalinclude:: ../tests/assets/uc_single_value_object.yaml
   :language: yaml

.. code-block:: shell-session

   $ syntrend generate single_value_object.yaml
   {"field_1": "9d3bl12", "field_2": -95, "field_3": 125.221053, "field_4": "large"}

Multiple Objects
````````````````

Creating multiple objects is simple by defining object names for each Object Definition.

.. literalinclude:: ../tests/assets/uc_multi_object.yaml
   :language: yaml

.. TODO: show new example of output

Multiple Objects to Outputs
```````````````````````````



Sequences
---------

Allowing any object to become a sequence is achieved through the `output` property on the Object Definition,
and allows you to define how many records should be generated.

Simple Sequence
```````````````

Creating a sequence of 5 randomly generated strings

.. literalinclude:: ../tests/assets/uc_multi_value_string.yaml
   :language: yaml
   :emphasize-lines: 2-3

.. code-block:: shell-session

   $ syntrend generate multi_value_string.yaml
   "tw3o094m8CFdaKYtE"
   "7v6nkAUeFhH0T"
   "EIdNLEA"
   "FXrf9L31BcbE1YGsTK"
   "ZbaY7IjAtdfMHLICI9L"

Constants Across Records
````````````````````````

Some cases require a dataset where a value must be consistent across the dataset. This ensures a
level of consistency where multiple values/records should contain the same value.

This is achieved through the `static` property type, though an alternative method also exists using
the expression look-back method below

.. TODO: Add chart of static values over sequence

Using this in a project could look like this:

.. literalinclude:: ../tests/assets/uc_static_ref_events.yaml
   :language: yaml

.. code-block::

   $ syntrend generate static_events.yaml
   {"timestamp": 1721376678, "user_id": "jdoe", "value": 101}
   {"timestamp": 1721376683, "user_id": "jdoe", "value": -241}
   {"timestamp": 1721376688, "user_id": "jdoe", "value": -367}
   {"timestamp": 1721376693, "user_id": "jdoe", "value": 307}
   {"timestamp": 1721376698, "user_id": "jdoe", "value": 300}

Alternatively, it's also possible to have `syntrend` generate a random starting value and re-use it like a
static value. The only different is instead of using the `static` type and `value` property, use the type of
choice and set `expression` to copy the last value.

.. literalinclude:: ../tests/assets/uc_static_ref_random_start.yaml
   :language: yaml

.. code-block::

   $ syntrend generate static_events.yaml
   {"timestamp": 1721455177, "user_id": "mdt", "value": -222}
   {"timestamp": 1721455182, "user_id": "mdt", "value": -136}
   {"timestamp": 1721455187, "user_id": "mdt", "value": 262}
   {"timestamp": 1721455192, "user_id": "mdt", "value": 364}
   {"timestamp": 1721455197, "user_id": "mdt", "value": -231}

Conditional Logic
`````````````````

It's possible to implement conditional logic to allow for static values that change within the dataset.

.. literalinclude:: ../tests/assets/uc_cond_status_change.yaml
   :language: yaml
   :emphasize-lines: 10
   :name: yaml_cond_status_change

Note the use of the parent object reference and the property to pull (`this().sensor`)

.. code-block::

   $ syntrend generate conditional_status.yaml
   {"ref": "status", "status": "below", "sensor": 0}
   {"ref": "status", "status": "below", "sensor": 2}
   {"ref": "status", "status": "below", "sensor": 4}
   {"ref": "status", "status": "above", "sensor": 6}
   {"ref": "status", "status": "above", "sensor": 8}

Numerical Trends
````````````````

Creating numerical trends/patterns in your projects are provided through the use of the `expression` property and using the previous values using the current object's offset parameter.

.. literalinclude:: ../tests/assets/uc_num_trend.yaml
   :language: yaml
   :name: yaml_num_trend

.. code-block::

   $ syntrend generate numerical_trend.yaml
   1
   2
   3
   4
   5

.. important:: Unlike charting expressions, you wouldn't have known XY values to calculate for familiar expressions. For example, generating a sine wave function requires some creativity. Using the `interval` value or timestamp offsets are helpful in these situations.

The following example will generate a single wave length of a sine wave with an amplitude of 20 and a frequency of approximately 10.

.. literalinclude:: ../tests/assets/uc_sine_wave.yaml
   :language: yaml
   :name: yaml_sine_wave
   :emphasize-lines: 4

.. code-block::

   $ syntrend generate numerical_trend.yaml
   5
   17.18369803069737
   20.719379013633127
   20.092974268256818
   15.57272626635812
   9.094320371245146
   3.4319750469207175
   1.0104508290207175
   2.8667060843242
   8.205845018010741

The added benefit to this is any other value in the project will have a constant set of values to refer and repeatable.

Simulating Events
`````````````````

By defining the field which includes the object's timestamp, it's possible to render a dataset as a real-time replay of events.

