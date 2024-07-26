"""DeepL translator component."""

from typing import Any, Dict, List, Optional, Union

from deepl import Formality, TextResult, Translator
from haystack import Document, component, default_from_dict, default_to_dict
from haystack.utils import Secret, deserialize_secrets_inplace


@component
class DeepLTextTranslator:
    """Enables translation of text using DeepL API."""

    def __init__(
        self,
        api_key: Secret = Secret.from_env_var("DEEPL_API_KEY"),  # noqa: B008
        source_lang: Optional[str] = None,
        target_lang: str = "EN-US",
        formality: Union[str, Formality, None] = None,
    ):
        """Create a DeepLTextTranslator component.

        Args:
            api_key: DeepL API Authentication Key.
            source_lang: Language code of the input text, e.g. "DE"
                for German, or "ES" for Spanish.
            target_lang: Language code to translate the text into,
                defaults to "EN", for English.
            formality: Desired formality for translation, as
            Formality enum, "less", "more", "prefer_less",
            "prefer_more", or "default".

        """
        self.api_key: Secret = api_key
        self.client: Translator = Translator(auth_key=self.api_key.resolve_value())
        self.source_lang: Optional[str] = source_lang
        self.target_lang: str = target_lang
        self.formality: Formality = Formality(formality or Formality.DEFAULT)

    @component.output_types(translation=str, meta=Dict[str, Any])
    def run(self, text: str, source_lang: Optional[str] = None):
        """Translate a single string.

        Args:
            text: Text to translate.
            source_lang: Language code of the input text, e.g. "DE"
                for German, or "ES" for Spanish. If informed, takes
                precedence over the `source_lang` informed at
                initialization.

        Returns: A dictionary with the following keys:
            - `translation`: The translation of the input text.
            - `meta`: Information about the usage of the model.

        """
        if not isinstance(text, str):
            raise TypeError(
                "DeepLTextTranslator expects a string as an input. "
                "In case you want to translate a list of Documents, "
                "please use the DeepLDocumentTranslator."
            )

        translation = self.client.translate_text(
            text,
            source_lang=source_lang or self.source_lang or None,
            target_lang=self.target_lang,
            formality=self.formality,
        )
        assert isinstance(translation, TextResult)
        meta = {
            "source_lang": translation.detected_source_lang,
            "language": self.target_lang,
        }
        return {"translation": translation.text, "meta": meta}

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the component to a dictionary.

        Returns: Dictionary with serialized data.

        """
        return default_to_dict(
            self,
            api_key=self.api_key.to_dict(),
            source_lang=self.source_lang,
            target_lang=self.target_lang,
            formality=self.formality.value,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeepLTextTranslator":
        """Deserializes the component from a dictionary.

        Args:
            data: Dictionary to deserialize from.

        Returns: Deserialized component.

        """
        deserialize_secrets_inplace(data["init_parameters"], keys=["api_key"])
        return default_from_dict(cls, data)


@component
class DeepLDocumentTranslator:
    """Enables translation of Haystack Documents using DeepL API."""

    def __init__(
        self,
        api_key: Secret = Secret.from_env_var("DEEPL_API_KEY"),  # noqa: B008
        source_lang: Optional[str] = None,
        target_lang: str = "EN-US",
        formality: Union[str, Formality, None] = None,
    ):
        """Create a DeepLDocumentTranslator component.

        Args:
            api_key: DeepL API Authentication Key.
            source_lang: Language code of the input text, e.g. "DE"
                for German, or "ES" for Spanish.
            target_lang: Language code to translate the text into,
                defaults to "EN", for English.
            formality: Desired formality for translation, as
            Formality enum, "less", "more", "prefer_less",
            "prefer_more", or "default".

        """
        self.api_key: Secret = api_key
        self.client: Translator = Translator(auth_key=self.api_key.resolve_value())
        self.source_lang: Optional[str] = source_lang
        self.target_lang: str = target_lang
        self.formality: Formality = Formality(formality or Formality.DEFAULT)

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document], source_lang: Optional[str] = None):
        """Translate a list of Haystack Documents.

        Args:
            documents: Documents to translate.
            source_lang: Language code of the input documents text,
                e.g. "DE" for German, or "ES" for Spanish. If informed,
                takes precedence over the `source_lang` informed at
                initialization.

        Returns: A list of documents with the translated text.
            Original document metadata is preserved.

        """
        if not (
            isinstance(documents, list)
            and all(isinstance(doc, Document) for doc in documents)
        ):
            raise TypeError(
                "DeepLTextTranslator expects a list of Haystack documents as input."
            )

        translations = self.client.translate_text(
            [doc.content for doc in documents],
            source_lang=source_lang or self.source_lang or None,
            target_lang=self.target_lang,
            formality=self.formality,
        )
        assert isinstance(translations, list)
        for _translation in translations:
            pass
        return {
            "documents": [
                Document(
                    content=translation.text,
                    meta=dict(
                        **document.meta,
                        source_lang=translation.detected_source_lang,
                        language=self.target_lang,
                    ),
                )
                for document, translation in zip(documents, translations)
            ]
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the component to a dictionary.

        Returns: Dictionary with serialized data.

        """
        return default_to_dict(
            self,
            api_key=self.api_key.to_dict(),
            source_lang=self.source_lang,
            target_lang=self.target_lang,
            formality=self.formality.value,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeepLTextTranslator":
        """Deserializes the component from a dictionary.

        Args:
            data: Dictionary to deserialize from.

        Returns: Deserialized component.

        """
        deserialize_secrets_inplace(data["init_parameters"], keys=["api_key"])
        return default_from_dict(cls, data)
