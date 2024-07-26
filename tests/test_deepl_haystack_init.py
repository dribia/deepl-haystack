"""Top level test suite."""

import re
import sys
from importlib import reload
from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

import deepl_haystack


class TestInit:
    @patch("importlib.metadata.version", side_effect=PackageNotFoundError)
    def test_version_not_found(self, mock_version):
        """Test `__version__` when the package is not found."""
        if "deepl_haystack" in sys.modules:
            del sys.modules["deepl_haystack"]
        import deepl_haystack

        reload(deepl_haystack)
        assert deepl_haystack.__version__ == "unknown"

    @patch("importlib.metadata.version")
    def test_version_found(self, mock_version):
        """Test `__version__` when the package is found."""
        mock_version.return_value = "0.1.0"
        if "deepl_haystack" in sys.modules:
            del sys.modules["deepl_haystack"]
        import deepl_haystack

        reload(deepl_haystack)
        assert deepl_haystack.__version__ == "0.1.0"

    def test_version(self):
        """Test the actual `__version__` value is valid."""
        assert (
            re.match(r"\d.\d.\d", deepl_haystack.__version__)
            or deepl_haystack.__version__ == "unknown"
        )
