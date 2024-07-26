"""Test cases for DeepL translator components."""

import os
from typing import Any

import pytest
from deepl import DeepLException, Formality, Translator
from haystack.utils import Secret

from deepl_haystack import DeepLTextTranslator

from .conftest import DEFAULT_SOURCE_LANG


class TestDeepLTextTranslator:
    """Test cases for the DeepLTextTranslator class."""

    _MISSING_API_KEY_REASON: str = (
        "Export an env var called DEEPL_API_KEY containing "
        "the DeepL API key to run this test."
    )

    def test_init_default(self, monkeypatch):
        """Default initialization of the DeepLTextTranslator class."""
        monkeypatch.setenv("DEEPL_API_KEY", "test-api-key")
        component = DeepLTextTranslator()
        assert isinstance(component.client, Translator)
        assert "test-api-key" in component.client.headers["Authorization"]
        assert component.formality is Formality.DEFAULT
        assert component.target_lang == "EN-US"
        assert component.source_lang is None

    def test_init_fail_wo_api_key(self, monkeypatch):
        monkeypatch.delenv("DEEPL_API_KEY", raising=False)
        with pytest.raises(
            ValueError, match="None of the .* environment variables are set"
        ):
            DeepLTextTranslator()

    def test_init_with_parameters(self, monkeypatch):
        monkeypatch.setenv("OPENAI_TIMEOUT", "100")
        monkeypatch.setenv("OPENAI_MAX_RETRIES", "10")
        component = DeepLTextTranslator(
            api_key=Secret.from_token("test-api-key"),
            source_lang="DE",
            target_lang="ES",
            formality="more",
        )
        assert isinstance(component.client, Translator)
        assert "test-api-key" in component.client.headers["Authorization"]
        assert component.source_lang == "DE"
        assert component.target_lang == "ES"
        assert component.formality is Formality.MORE

    def test_to_dict_default(self, monkeypatch):
        monkeypatch.setenv("DEEPL_API_KEY", "test-api-key")
        component = DeepLTextTranslator()
        data = component.to_dict()
        assert data == {
            "type": "deepl_haystack.components.translators.deepl.translator.DeepLTextTranslator",
            "init_parameters": {
                "api_key": {
                    "env_vars": ["DEEPL_API_KEY"],
                    "strict": True,
                    "type": "env_var",
                },
                "source_lang": None,
                "target_lang": "EN-US",
                "formality": Formality.DEFAULT.value,
            },
        }

    def test_to_dict_with_parameters(self, monkeypatch):
        monkeypatch.setenv("ENV_VAR", "test-api-key")
        component = DeepLTextTranslator(
            api_key=Secret.from_env_var("ENV_VAR"),
            source_lang="DE",
            target_lang="ES",
            formality="more",
        )
        data = component.to_dict()
        assert data == {
            "type": "deepl_haystack.components.translators.deepl.translator.DeepLTextTranslator",
            "init_parameters": {
                "api_key": {"env_vars": ["ENV_VAR"], "strict": True, "type": "env_var"},
                "source_lang": "DE",
                "target_lang": "ES",
                "formality": Formality.MORE.value,
            },
        }

    def test_from_dict(self, monkeypatch):
        monkeypatch.setenv("DEEPL_API_KEY", "test-api-key")
        data = {
            "type": "deepl_haystack.components.translators.deepl.translator.DeepLTextTranslator",
            "init_parameters": {
                "api_key": {
                    "env_vars": ["DEEPL_API_KEY"],
                    "strict": True,
                    "type": "env_var",
                },
                "source_lang": "DE",
                "target_lang": "ES",
                "formality": Formality.MORE.value,
            },
        }
        component = DeepLTextTranslator.from_dict(data)
        assert component.source_lang == "DE"
        assert component.target_lang == "ES"
        assert component.formality is Formality.MORE
        assert component.api_key == Secret.from_env_var("DEEPL_API_KEY")

    def test_from_dict_fail_wo_env_var(self, monkeypatch):
        monkeypatch.delenv("DEEPL_API_KEY", raising=False)
        data = {
            "type": "deepl_haystack.components.translators.deepl.translator.DeepLTextTranslator",
            "init_parameters": {
                "api_key": {
                    "env_vars": ["DEEPL_API_KEY"],
                    "strict": True,
                    "type": "env_var",
                },
                "source_lang": "DE",
                "target_lang": "ES",
                "formality": Formality.MORE.value,
            },
        }
        with pytest.raises(
            ValueError, match="None of the .* environment variables are set"
        ):
            DeepLTextTranslator.from_dict(data)

    def test_run(self, monkeypatch, mock_translation):
        """Test the run method of the DeepLTextTranslator class."""
        monkeypatch.setenv("DEEPL_API_KEY", "fake-api-key")
        target_lang = "ES"
        text = "What's Natural Language Processing?"
        formality = "more"
        component = DeepLTextTranslator(
            source_lang=DEFAULT_SOURCE_LANG,
            target_lang=target_lang,
            formality=formality,
        )
        response = component.run(text)

        mock_translation.assert_called_once_with(
            text,
            source_lang=DEFAULT_SOURCE_LANG,
            target_lang=target_lang,
            formality=Formality(formality),
        )
        assert isinstance(response, dict)
        assert "translation" in response
        assert response["translation"] == text
        assert "meta" in response
        assert "source_lang" in response["meta"]
        assert "language" in response["meta"]
        assert response["meta"]["source_lang"] == DEFAULT_SOURCE_LANG
        assert response["meta"]["language"] == "ES"

    def test_run_with_source_lang(self, monkeypatch, mock_translation):
        """Test the run method of the DeepLTextTranslator class."""
        monkeypatch.setenv("DEEPL_API_KEY", "fake-api-key")
        target_lang = "ES"
        source_lang = "IT"
        text = "What's Natural Language Processing?"
        formality = "more"
        component = DeepLTextTranslator(
            source_lang=source_lang,
            target_lang=target_lang,
            formality=formality,
        )
        response = component.run(text)

        mock_translation.assert_called_once_with(
            text,
            source_lang=source_lang,
            target_lang=target_lang,
            formality=Formality(formality),
        )
        assert isinstance(response, dict)
        assert "meta" in response
        assert "source_lang" in response["meta"]
        assert "language" in response["meta"]
        assert response["meta"]["language"] == "ES"

    @pytest.mark.parametrize(
        "wrong_input", [1, ["one string", "other string"], object, object()]
    )
    def test_run_wrong_input(self, monkeypatch, wrong_input: Any):
        """Test the run method of the DeepLDocumentTranslator class.

        Tests the single document use case.

        """
        monkeypatch.setenv("DEEPL_API_KEY", "fake-api-key")
        component = DeepLTextTranslator(
            source_lang=DEFAULT_SOURCE_LANG,
            target_lang="ES",
        )
        with pytest.raises(
            TypeError,
            match=(
                "DeepLTextTranslator expects a string as an input. "
                "In case you want to translate a list of Documents, "
                "please use the DeepLDocumentTranslator."
            ),
        ):
            component.run(wrong_input)

    @pytest.mark.skipif(
        not os.environ.get("DEEPL_API_KEY", None),
        reason=_MISSING_API_KEY_REASON,
    )
    @pytest.mark.integration
    def test_live_run(self):
        component = DeepLTextTranslator(
            source_lang="EN",
            target_lang="ES",
        )
        results = component.run("What's the capital of France?")
        assert results["translation"] == "¿Cuál es la capital de Francia?"
        assert results["meta"]["source_lang"] == "EN"
        assert results["meta"]["target_lang"] == "ES"

    @pytest.mark.skipif(
        not os.environ.get("DEEPL_API_KEY", None),
        reason=_MISSING_API_KEY_REASON,
    )
    @pytest.mark.integration
    def test_live_run_wrong_source_language(self):
        component = DeepLTextTranslator(source_lang="something-wrong")
        with pytest.raises(
            DeepLException, match=r".* Value for 'source_lang' not supported."
        ):
            component.run("Whatever")

    @pytest.mark.skipif(
        not os.environ.get("DEEPL_API_KEY", None),
        reason=_MISSING_API_KEY_REASON,
    )
    @pytest.mark.integration
    def test_live_run_wrong_target_language(self):
        component = DeepLTextTranslator(target_lang="something-wrong")
        with pytest.raises(
            DeepLException, match=r".* Value for 'target_lang' not supported."
        ):
            component.run("Whatever")
