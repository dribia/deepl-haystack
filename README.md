DeepL Haystack Integration
==========================

|         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CI/CD   | [![Tests](https://github.com/dribia/deepl-haystack/actions/workflows/test.yml/badge.svg)](https://github.com/dribia/deepl-haystack/actions/workflows/test.yml) [![Coverage Status](https://img.shields.io/codecov/c/github/dribia/driconfig)](https://codecov.io/gh/dribia/driconfig) [![Tests](https://github.com/dribia/deepl-haystack/actions/workflows/lint.yml/badge.svg)](https://github.com/dribia/deepl-haystack/actions/workflows/lint.yml) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) |
| Package | [![PyPI](https://img.shields.io/pypi/v/deepl-haystack)](https://pypi.org/project/deepl-haystack/) ![PyPI - Downloads](https://img.shields.io/pypi/dm/deepl-haystack?color=blue&logo=pypi&logoColor=gold) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/deepl-haystack?logo=python&logoColor=gold) [![GitHub](https://img.shields.io/github/license/dribia/deepl-haystack?color=blue)](LICENSE)                                                                                                                                                                                |
---

**Table of Contents**

- [deepl-haystack](#deepl-haystack-integration)
  - [Installation](#installation)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

```console
pip install deepl-haystack
```

## Contributing

[Poetry](https://python-poetry.org) is the best way to interact with this project, to install it,
follow the official [Poetry installation guide](https://python-poetry.org/docs/#installation).

With `poetry` installed, one can install the project dependencies with:

```shell
poetry install
```

Then, to run the project unit tests:

```shell
make test-unit
```

To run the linters (`ruff` and `mypy`):

```shell
make lint
```

To apply all code formatting:

```shell
make format
```

And finally, to run the project integration tests (which actually use the DeepL API),
you should either have the `DEEPL_API_KEY` environment variable set,
or create a `.env` file:

```dotenv
DEEPL_API_KEY=your_api_key_here
```

And run:

```shell
make test-integration
```

## License

`deepl-haystack` is distributed under the terms of the
[MIT](https://opensource.org/license/mit) license.
