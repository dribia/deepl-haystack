"""DeepL Haystack integration."""

from importlib.metadata import PackageNotFoundError, version

from .components.translators.deepl.translator import (
    DeepLDocumentTranslator,
    DeepLTextTranslator,
)

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["DeepLDocumentTranslator", "DeepLTextTranslator"]
