"""Test suite configuration."""

from collections.abc import Iterable
from typing import Union
from unittest.mock import MagicMock, patch

import pytest
from deepl import Formality, Language, TextResult, Translator

DEFAULT_SOURCE_LANG = "DE"


def translate_text_mock(
    text: Union[str, Iterable[str]],
    *,
    target_lang: Union[str, Language],
    source_lang: Union[str, Language, None] = None,
    formality: Union[str, Formality, None] = None,
    **kwargs,
):
    """Mock the DeepL API translation response.

    Returns: Mock object for the DeepL API translation response.

    """
    if isinstance(text, str):
        return TextResult(
            text=text,
            detected_source_lang=source_lang or DEFAULT_SOURCE_LANG,
            billed_characters=len(text),
        )
    return [
        TextResult(text=t, detected_source_lang="DE", billed_characters=len(t))
        for t in text
    ]


@pytest.fixture
def mock_translation():
    """Mock the DeepL API translation response.

    This fixture allows to reuse the same response in multiple tests.

    Returns: Mock object for the DeepL API translation response.

    """
    with patch.object(
        Translator, "translate_text", new_callable=MagicMock
    ) as mock_method:
        mock_method.side_effect = translate_text_mock
        yield mock_method
