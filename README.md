# Syntrend Synthetic Data Generation

Syntrend is a Python Package and Command Line tool for generating synthetic data to express very specific behaviours and trends across multiple inputs.

[![Tests](https://github.com/wsidl/syntrend/actions/workflows/test.yaml/badge.svg)](https://github.com/wsidl/syntrend/actions/workflows/test.yaml)
<!-- Add Badges --> 

A simple Project may only contain a few lines of YAML

```shell
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
```

---

Specific objectives for this project is to:

- **Be Lightweight**: Make a tool that can easily run from a local workstation, from a CI Pipeline, or embedded into an application.
- **Be Easy to Use**: All configurations use YAML, intended as an extendable markup format that allows re-use within and across projects.
- **Be Environment Agnostic**: Everyone has preferences of how they want to work so providing formatted outputs that can be easily consumed by target sources is necessary.
- **Support *As Many* Data Types As Possible**: Projects have different expectations of how they consume data: exchange formats, structured, streaming, or a combination of all with references between them.
- **Be Expressive**: Data can have a personality, and we need this data to express that personality so we have something consistent to work with.

## Quickstart

1. Install Syntrend

    For a local Python project, use the project release to PyPI
    
    ```shell
    pip install syntrend
    ```
    
    or pull the Docker image
    
    ```shell
    docker pull ghcr.io/wsidl/syntrend:latest
    ```

2. Create a Project File

    Create a text file with the YAML content defined in the Project File structure
    
    ```yaml
    type: string
    ```

3. Run the Project File

    ```shell
    syntrend generate project_file.yaml
    ```
   
    if using Docker:

    ```shell
    docker run -v $(pwd):/project -w /project ghcr.io/wsidl/syntrend:latest generate project_file.yaml
    ```

4. Handle the data

    The data can be produced into a number of different locations. This can be handled after the command is generated or piped from the outputs.

## Next Steps

- Become familiar with [Project File structure](docs/project_file.md)
- Review the [types of data generators](docs/generators.md) that can create and parse values for the dataset
- Understand how to use [Expressions](docs/expressions.md) to define trends in specific properties across a project.
- Apply controlled randomness within your data using [Value Distributions](docs/distributions.md)
- Understand how data can be [formatted or provide custom outputs](docs/outputs.md)
- Read the [FAQ's](docs/faq.md) for any un-answered questions

## Contributing

see [CONTRIBUTING](docs/contributing.md) documentation
