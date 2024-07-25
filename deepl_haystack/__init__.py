"""DeepL Haystack integration."""

from .components.translators.deepl.translator import (
    DeepLDocumentTranslator,
    DeepLTextTranslator,
)

__version__ = "0.1.1"

__all__ = ["DeepLDocumentTranslator", "DeepLTextTranslator"]
