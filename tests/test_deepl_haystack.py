"""Top level test suite."""

import re

import deepl_haystack


def test_version():
    """Assert that `__version__` exists and is valid."""
    assert re.match(r"\d.\d.\d", deepl_haystack.__version__)
