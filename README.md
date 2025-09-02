DeepL Haystack Integration
==========================

<p align="left">
    <em>Haystack integration with DeepL translation services provider.</em>
</p>

|         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CI/CD   | [![Tests](https://github.com/dribia/deepl-haystack/actions/workflows/test.yml/badge.svg)](https://github.com/dribia/deepl-haystack/actions/workflows/test.yml) [![Coverage Status](https://img.shields.io/codecov/c/github/dribia/deepl-haystack)](https://codecov.io/gh/dribia/deepl-haystack) [![Tests](https://github.com/dribia/deepl-haystack/actions/workflows/lint.yml/badge.svg)](https://github.com/dribia/deepl-haystack/actions/workflows/lint.yml) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) |
| Package | [![PyPI](https://img.shields.io/pypi/v/deepl-haystack)](https://pypi.org/project/deepl-haystack/) ![PyPI - Downloads](https://img.shields.io/pypi/dm/deepl-haystack?color=blue&logo=pypi&logoColor=gold) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/deepl-haystack?logo=python&logoColor=gold) [![GitHub](https://img.shields.io/github/license/dribia/deepl-haystack?color=blue)](LICENSE)                                                                                                                                                                                                                                                                                                                |
---

**Documentation**: [https://haystack.deepset.ai/integrations/deepl](https://haystack.deepset.ai/integrations/deepl)

**Source Code**: [https://github.com/dribia/deepl-haystack](https://github.com/dribia/deepl-haystack)

---

## Installation

This project resides in the Python Package Index (PyPI), so it can easily be installed with `pip`:

```console
pip install deepl-haystack
```

## Usage

The DeepL Haystack integration provides two Haystack components: `DeepLTextTranslator`
and `DeepLDocumentTranslator`. These components can be used to translate text and documents,
respectively, using the DeepL API.

## Examples

To run these examples you'll need a working DeepL API key.
You can get one by signing up at the [DeepL API website](https://www.deepl.com/pro#developer).

### Standalone Text Translation

```python
from haystack.utils import Secret

from deepl_haystack import DeepLTextTranslator

translator = DeepLTextTranslator(
    api_key=Secret.from_token("your_api_key_here"), source_lang="EN", target_lang="ES"
)

translated_text = translator.run("Hello, world!")
print(translated_text)
# {'translation': '¡Hola, mundo!', 'meta': {'source_lang': 'EN', 'target_lang': 'ES'}}
```

### Standalone Document Translation

```python
from haystack.dataclasses import Document
from haystack.utils import Secret

from deepl_haystack import DeepLDocumentTranslator

translator = DeepLDocumentTranslator(
    api_key=Secret.from_token("your_api_key_here"), source_lang="EN", target_lang="ES"
)

documents_to_translate = [
    Document(content="Hello, world!"),
    Document(content="Goodbye, Joe!", meta={"name": "Joe"}),
]

translated_documents = translator.run(documents_to_translate)
print("\n".join([f"{doc.content}, {doc.meta}" for doc in translated_documents]))
# ¡Hola, mundo!, {'source_lang': 'EN', 'target_lang': 'ES'}
# ¡Adiós, Joe!, {'name': 'Joe', 'source_lang': 'EN', 'target_lang': 'ES'}
```

### Haystack Pipeline Integration

```python
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.writers import DocumentWriter
from haystack.dataclasses.byte_stream import ByteStream
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.utils import Secret

from deepl_haystack import DeepLDocumentTranslator

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component(instance=TextFileToDocument(), name="converter")
pipeline.add_component(
    instance=DeepLDocumentTranslator(
        api_key=Secret.from_token("your_api_key_here"),
        target_lang="ES",
    ),
    name="translator",
)
pipeline.add_component(
    instance=DocumentWriter(document_store=document_store), name="document_store"
)
pipeline.connect("converter", "translator")
pipeline.connect("translator", "document_store")
pipeline.run({"converter": {"sources": [ByteStream.from_string("Hello world!")]}})
print(document_store.filter_documents())
# [Document(id=..., content: '¡Hola, mundo!', meta: {'source_lang': 'EN', 'language': 'ES'})]
```

## Contributing

[uv](https://docs.astral.sh/uv/) is the best way to interact with this project, to install it,
follow the official [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

With `uv` installed, one can install the project dependencies with:

```shell
uv sync
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
Check the [LICENSE](./LICENSE) file for further details.
