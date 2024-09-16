Value Trend Distribution
========================

The dominant feature of this utility is its ability to generate datasets to express
a known pattern or behaviour based on an algorithm or expression. These expressions can be leveraged
for a number of use cases, described here. In particular to this document is the ability to provide a
level of "fuzziness" to that data to generate datasets to best mimic the uncertain nature of real data.
This is done by applying a randomized offset to the generated value so that it can resemble real data
while resembling a known pattern or expression.

To apply a value distribution in your configuration, the target property definition must include the
`distribution` sub-property with relevant nested configurations provided.

.. important::

    Any examples provided assumes that...

    * A Project Config generates an object sequence with more than 1 value (`output.count > 1`)
    * The value being used is a numerical primitive (integer or float/double)

.. note::

    It is not required for the property to use an `expression` for a value distribution to apply.
    Randomly-generated values can have an additional distribution applied to it.

No Distribution
---------------

This is the default behaviour for all generated values.
If you apply an expression, it will generate a value as you expect by the expression.

For example, if a value generator was provided an expression:

.. code-block:: yaml

    output:
      count: 30
    type: static
    value: 5.0

The resulting dataset would plot out a constant of 5 for all values

.. code-block:: shell-session

    $ syntrend generate static_values.yaml
    5.0
    5.0
    5.0
    5.0
    5.0
    ...

Plotting these values would give something similar to the following:

.. plot:: _diag/distribution_graph.py none


Linear Distribution
-------------------

Applying some randomization to your values enables variance in your data
while keeping the data close to the expected behaviour it's intended to reflect.

How this looks in a Project File from the previous example is the introduction of a `distribution` property with
definitions of how to vary the data.

.. code-block:: yaml
    :emphasize-lines: 3-6

    output:
        count: 30
    distribution:
        type: linear
        min_offset: -3
        max_offset: 5
    type: static
    value: 5.0

Generating a dataset from this results in a non-linear progression

.. code-block:: shell-session

    $ syntrend generate lin_dist_values.yaml
    3.4286597355069164
    2.759552727927165
    5.139106683692621
    7.846772286339835
    4.370221795766835
    ...

Plotting these values would give something similar to the following:

.. plot:: _diag/distribution_graph.py linear


Standard Deviation Distribution
-------------------------------

Sometimes variance is not so linear and you need datasets that will occasionally (rarely)
produce an outlier value or provide values that cluster closer to the expected
trend. This is where applying a Standard Deviation Distribution can help.

Building from the previous example, we'll apply the `std_dev` distribution type
with a `std_dev` value (or Standard Deviation value) to denote the spread of the distribution.

.. code-block:: yaml
    :emphasize-lines: 4-5

    output:
        count: 30
    distribution:
        type: std_dev
        std_dev: 2
    type: integer
    expression: interval + 5

.. code-block:: shell-session

    $ syntrend generate sd_distributed_values.yaml
    6.539895504932106
    5.864296778185984
    6.58124836310444
    1.5985193382969385
    4.711970924784011
    ...

.. plot:: _diag/distribution_graph.py std_dev
