"""Test cases for DeepL translator components."""

import os
from typing import Any

import pytest
from deepl import DeepLException, Formality, Translator
from haystack import Document
from haystack.utils import Secret

from deepl_haystack import DeepLDocumentTranslator

from .conftest import DEFAULT_SOURCE_LANG


class TestDeepLDocumentTranslator:
    """Test cases for the DeepLDocumentTranslator class."""

    _MISSING_API_KEY_REASON: str = (
        "Export an env var called DEEPL_API_KEY containing "
        "the DeepL API key to run this test."
    )

    def test_init_default(self, monkeypatch):
        """Default initialization of the DeepLDocumentTranslator class."""
        monkeypatch.setenv("DEEPL_API_KEY", "test-api-key")
        component = DeepLDocumentTranslator()
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
            DeepLDocumentTranslator()

    def test_init_with_parameters(self, monkeypatch):
        monkeypatch.setenv("OPENAI_TIMEOUT", "100")
        monkeypatch.setenv("OPENAI_MAX_RETRIES", "10")
        component = DeepLDocumentTranslator(
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
        component = DeepLDocumentTranslator()
        data = component.to_dict()
        assert data == {
            "type": "deepl_haystack.components.DeepLDocumentTranslator",
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
        component = DeepLDocumentTranslator(
            api_key=Secret.from_env_var("ENV_VAR"),
            source_lang="DE",
            target_lang="ES",
            formality="more",
        )
        data = component.to_dict()
        assert data == {
            "type": "deepl_haystack.components.DeepLDocumentTranslator",
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
            "type": "deepl_haystack.components.DeepLDocumentTranslator",
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
        component = DeepLDocumentTranslator.from_dict(data)
        assert component.source_lang == "DE"
        assert component.target_lang == "ES"
        assert component.formality is Formality.MORE
        assert component.api_key == Secret.from_env_var("DEEPL_API_KEY")

    def test_from_dict_fail_wo_env_var(self, monkeypatch):
        monkeypatch.delenv("DEEPL_API_KEY", raising=False)
        data = {
            "type": "deepl_haystack.components.DeepLDocumentTranslator",
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
            DeepLDocumentTranslator.from_dict(data)

    def test_run_one_doc(self, monkeypatch, mock_translation):
        """Test the run method of the DeepLDocumentTranslator class.

        Tests the single document use case.

        """
        monkeypatch.setenv("DEEPL_API_KEY", "fake-api-key")
        target_lang = "ES"
        text = "What's Natural Language Processing?"
        formality = "more"
        component = DeepLDocumentTranslator(
            source_lang=DEFAULT_SOURCE_LANG,
            target_lang=target_lang,
            formality=formality,
        )
        documents = [Document(content=text)]
        response = component.run(documents)
        mock_translation.assert_called_once_with(
            [text],
            source_lang=DEFAULT_SOURCE_LANG,
            target_lang=target_lang,
            formality=Formality(formality),
        )
        assert isinstance(response, dict)
        assert len(response) == 1
        assert "documents" in response
        assert isinstance(response["documents"], list)
        assert len(response["documents"]) == 1
        assert response["documents"][0].content == text
        assert "source_lang" in response["documents"][0].meta
        assert "language" in response["documents"][0].meta
        assert response["documents"][0].meta["source_lang"] == DEFAULT_SOURCE_LANG
        assert response["documents"][0].meta["language"] == "ES"

    def test_run_empty_list(self, monkeypatch, mock_translation):
        """Test the run method of the DeepLDocumentTranslator class.

        Tests the empty list use case.

        """
        monkeypatch.setenv("DEEPL_API_KEY", "fake-api-key")
        target_lang = "ES"
        formality = "more"
        component = DeepLDocumentTranslator(
            source_lang=DEFAULT_SOURCE_LANG,
            target_lang=target_lang,
            formality=formality,
        )
        documents = []
        response = component.run(documents)

        mock_translation.assert_called_once_with(
            [],
            source_lang=DEFAULT_SOURCE_LANG,
            target_lang=target_lang,
            formality=Formality(formality),
        )
        assert isinstance(response, dict)
        assert "documents" in response
        assert len(response) == 1
        assert isinstance(response["documents"], list)
        assert len(response["documents"]) == 0

    @pytest.mark.parametrize("wrong_input", [1, "string", object, object()])
    def test_run_wrong_input(self, monkeypatch, wrong_input: Any):
        """Test the run method of the DeepLDocumentTranslator class.

        Tests the single document use case.

        """
        monkeypatch.setenv("DEEPL_API_KEY", "fake-api-key")
        component = DeepLDocumentTranslator(
            source_lang=DEFAULT_SOURCE_LANG,
            target_lang="ES",
        )
        with pytest.raises(
            TypeError,
            match="DeepLTextTranslator expects a list of Haystack documents as input.",
        ):
            component.run(wrong_input)

    def test_run_preserves_meta(self, monkeypatch, mock_translation):
        """Test the run method of the DeepLDocumentTranslator class."""
        monkeypatch.setenv("DEEPL_API_KEY", "fake-api-key")
        text = "What's Natural Language Processing?"
        component = DeepLDocumentTranslator(target_lang="ES")
        meta = {"meta_1": "foo", "meta_2": "bar"}
        response = component.run([Document(content=text, meta=meta)])
        assert "source_lang" in response["documents"][0].meta
        assert "language" in response["documents"][0].meta
        assert "meta_1" in response["documents"][0].meta
        assert "meta_2" in response["documents"][0].meta
        assert response["documents"][0].meta["meta_1"] == "foo"
        assert response["documents"][0].meta["meta_2"] == "bar"

    @pytest.mark.skipif(
        not os.environ.get("DEEPL_API_KEY", None),
        reason=_MISSING_API_KEY_REASON,
    )
    @pytest.mark.integration
    def test_live_run(self):
        component = DeepLDocumentTranslator(
            source_lang="EN",
            target_lang="ES",
        )
        response = component.run([Document(content="What's the capital of France?")])
        assert response["documents"][0].content == "¿Cuál es la capital de Francia?"
        assert response["documents"][0].meta["source_lang"] == "EN"
        assert response["documents"][0].meta["language"] == "ES"

    @pytest.mark.skipif(
        not os.environ.get("DEEPL_API_KEY", None),
        reason=_MISSING_API_KEY_REASON,
    )
    @pytest.mark.integration
    def test_live_run_wrong_source_language(self):
        component = DeepLDocumentTranslator(source_lang="something-wrong")
        with pytest.raises(
            DeepLException, match=r".* Value for 'source_lang' not supported."
        ):
            component.run([Document(content="Whatever")])

    @pytest.mark.skipif(
        not os.environ.get("DEEPL_API_KEY", None),
        reason=_MISSING_API_KEY_REASON,
    )
    @pytest.mark.integration
    def test_live_run_wrong_target_language(self):
        component = DeepLDocumentTranslator(target_lang="something-wrong")
        with pytest.raises(
            DeepLException, match=r".* Value for 'target_lang' not supported."
        ):
            component.run([Document(content="Whatever")])
