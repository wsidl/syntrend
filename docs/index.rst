|project_title|
===============

Syntrend is a Python Package and Command Line tool for generating synthetic data to express very specific behaviours and trends across multiple inputs.

A simple Project looks like this.

.. code-block:: shell-session

    $ cat 5_numbers.yaml
    output:
      count: 5
    type: integer

    $ syntrend generate 5_numbers.yaml
    -178
    430
    -192
    -114
    -125

------------

Specific objectives for this project is to:

- **Be Lightweight**: Make a tool that can easily run from a local workstation, from a CI Pipeline, or embedded into an application.
- **Be Easy to Use**: All configurations use YAML, intended as an extendable markup format that allows re-use within and across projects.
- **Be Environment Agnostic**: Everyone has preferences of how they want to work so providing formatted outputs that can be easily consumed by target sources is necessary.
- **Support As Many Data Types As Possible**: Projects have different expectations of how they consume data: exchange formats, structured, streaming, or a combination of all with references between them.
- **Be Expressive**: Data can have a personality, and we need this data to express that personality so we have something consistent to work with.

Documentation
-------------

.. toctree::
   :maxdepth: 2

   quickstart
   project_file
   distributions
   expressions
   use_cases
   contributing
   faq