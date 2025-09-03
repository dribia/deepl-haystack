"""DeepL translator components."""

from typing import Any, Dict, List, Literal, Optional, Union

from deepl import (
    Formality,
    SplitSentences,
    TextResult,
    Translator,
    http_client,
)
from haystack import Document, component, default_from_dict, default_to_dict, logging
from haystack.utils import Secret, deserialize_secrets_inplace

logger = logging.getLogger(__name__)


@component
class DeepLTextTranslator:
    """Enables translation of text using DeepL API."""

    def __init__(
        self,
        api_key: Secret = Secret.from_env_var("DEEPL_API_KEY"),  # noqa: B008
        source_lang: Optional[str] = None,
        target_lang: str = "EN-US",
        formality: Union[str, Formality, None] = None,
        *,
        max_retries: int = 5,
        preserve_formatting: bool = False,
        split_sentences: Union[str, SplitSentences, None] = None,
        context: Optional[str] = None,
        glossary: Union[str, None] = None,
        tag_handling: Literal[None, "xml", "html"] = None,
        outline_detection: bool = True,
        non_splitting_tags: Union[str, List[str], None] = None,
        splitting_tags: Union[str, List[str], None] = None,
        ignore_tags: Union[str, List[str], None] = None,
    ):
        """Create a DeepLTextTranslator component.

        Args:
            api_key: DeepL API Authentication Key.
            source_lang: Language code of the input text, e.g. "DE"
                for German, or "ES" for Spanish.
            target_lang: Language code to translate the text into,
                defaults to "EN", for English.
            formality: Controls whether translations should lean toward
                informal or formal language. Can be expressed as a string
                or as a Formality enum. Possible values are "less", "more",
                "prefer_less", "prefer_more", or "default".
                This feature currently only works for the following languages:
                DE (German), FR (French), IT (Italian), ES (Spanish),
                NL (Dutch), PL (Polish), PT-BR and PT-PT (Portuguese),
                JA (Japanese), and RU (Russian).
            max_retries: Maximum number of network retries after a failed HTTP
                request. Default retries is set to 5.
            preserve_formatting: Controls automatic formatting correction.
                Set to `True` to prevent automatic correction of formatting.
            split_sentences: Controls how the translation engine should split
                input into sentences before translation. Can be expressed as
                a string or as a SplitSentences enum. Possible values are:
                - 0: 0 means OFF. No splitting at all, whole input is treated
                as one sentence. Use this option if the input text is already
                split into sentences, to prevent the engine from splitting the sentence
                unintentionally.
                - 1: 1 means ALL. (default) splits on punctuation and on newlines.
                - 'nonewlines': splits on punctuation only, ignoring newlines.
            context: Use this setting to include additional context that can
                influence a translation without being translated itself.
                Providing additional context can potentially improve translation
                quality, especially for short, low-context source texts such as
                product names on an e-commerce website, article headlines on a
                news website, or UI elements.
                For more information and examples, refer to the
                [DeepL API documentation](https://developers.deepl.com/docs/api-reference/translate).
            glossary: glossary ID to use for translation. Must match specified
                `source_lang` and `target_lang`.
            tag_handling: Optional type of tags to parse before translation.
                Only "xml" and "html" are currently available.
            outline_detection: Set to False to disable automatic tag detection.
            non_splitting_tags: XML tags that should not be used to split text
                into sentences.
            splitting_tags: XML tags that should be used to split text into
                sentences.
            ignore_tags: XML tags containing text that should not be translated.

        """
        if not isinstance(target_lang, str) or not target_lang:
            raise ValueError(
                "`target_lang` must be a string representing a language code. "
                "For more information about DeepL supported languages, "
                "see https://developers.deepl.com/docs/resources/supported-languages"
            )

        self.api_key: Secret = api_key
        self.max_retries: int = max_retries
        http_client.max_network_retries = self.max_retries
        self.client: Translator = Translator(auth_key=str(self.api_key.resolve_value()))

        self.source_lang: Optional[str] = source_lang
        self.target_lang: str = target_lang
        self.formality: Formality = Formality(formality or Formality.DEFAULT)
        self.preserve_formatting: bool = preserve_formatting
        self.split_sentences: SplitSentences = SplitSentences(
            split_sentences or SplitSentences.DEFAULT
        )
        self.context: Optional[str] = context
        self.glossary: Union[str, None] = glossary
        self.tag_handling: Literal[None, "xml", "html"] = tag_handling
        self.outline_detection: bool = outline_detection
        self.non_splitting_tags: Union[str, List[str], None] = non_splitting_tags
        self.splitting_tags: Union[str, List[str], None] = splitting_tags
        self.ignore_tags: Union[str, List[str], None] = ignore_tags

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

        if not text:
            raise ValueError("Empty text provided.")

        translation = self.client.translate_text(
            text,
            source_lang=source_lang or self.source_lang or None,
            target_lang=self.target_lang,
            formality=self.formality,
            preserve_formatting=self.preserve_formatting,
            split_sentences=self.split_sentences,
            context=self.context,
            glossary=self.glossary,
            tag_handling=self.tag_handling,
            outline_detection=self.outline_detection,
            non_splitting_tags=self.non_splitting_tags,
            splitting_tags=self.splitting_tags,
            ignore_tags=self.ignore_tags,
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
            preserve_formatting=self.preserve_formatting,
            split_sentences=self.split_sentences.value,
            context=self.context,
            glossary=self.glossary,
            tag_handling=self.tag_handling,
            outline_detection=self.outline_detection,
            non_splitting_tags=self.non_splitting_tags,
            splitting_tags=self.splitting_tags,
            ignore_tags=self.ignore_tags,
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
        target_lang: Union[str, List[str]] = "EN-US",
        formality: Union[str, Formality, None] = None,
        *,
        max_retries: int = 5,
        preserve_formatting: bool = False,
        split_sentences: Union[str, SplitSentences, None] = None,
        context: Optional[str] = None,
        glossary: Union[str, None] = None,
        tag_handling: Literal[None, "xml", "html"] = None,
        outline_detection: bool = True,
        non_splitting_tags: Union[str, List[str], None] = None,
        splitting_tags: Union[str, List[str], None] = None,
        ignore_tags: Union[str, List[str], None] = None,
        include_score: bool = True,
    ):
        """Create a DeepLDocumentTranslator component.

        Args:
            api_key: DeepL API Authentication Key.
            source_lang: Language code of the input text, e.g. "DE"
                for German, or "ES" for Spanish.
            target_lang: Language code to translate the text into, or a list of
                language codes. Defaults to "EN", for English.
                If multiple languages are specified, a translated document is
                returned for each language.
            formality: Controls whether translations should lean toward
                informal or formal language. Can be expressed as a string
                or as a Formality enum. Possible values are "less", "more",
                "prefer_less", "prefer_more", or "default".
                This feature currently only works for the following languages:
                DE (German), FR (French), IT (Italian), ES (Spanish),
                NL (Dutch), PL (Polish), PT-BR and PT-PT (Portuguese),
                JA (Japanese), and RU (Russian).
            max_retries: Maximum number of network retries after a failed HTTP
                request. Default retries is set to 5.
            preserve_formatting: Controls automatic formatting correction.
                Set to `True` to prevent automatic correction of formatting.
            split_sentences: Controls how the translation engine should split
                input into sentences before translation. Can be expressed as
                a string or as a SplitSentences enum. Possible values are:
                - 0: 0 means OFF. No splitting at all, whole input is treated
                as one sentence. Use this option if the input text is already
                split into sentences, to prevent the engine from splitting the sentence
                unintentionally.
                - 1: 1 means ALL. (default) splits on punctuation and on newlines.
                - 'nonewlines': splits on punctuation only, ignoring newlines.
            context: Use this setting to include additional context that can
                influence a translation without being translated itself.
                Providing additional context can potentially improve translation
                quality, especially for short, low-context source texts such as
                product names on an e-commerce website, article headlines on a
                news website, or UI elements.
                For more information and examples, refer to the
                [DeepL API documentation](https://developers.deepl.com/docs/api-reference/translate).
            glossary: glossary ID to use for translation. Must match specified
                `source_lang` and `target_lang`.
            tag_handling: Optional type of tags to parse before translation.
                Only "xml" and "html" are currently available.
            outline_detection: Set to False to disable automatic tag detection.
            non_splitting_tags: XML tags that should not be used to split text
                into sentences.
            splitting_tags: XML tags that should be used to split text into
                sentences.
            ignore_tags: XML tags containing text that should not be translated.
            include_score: Whether to include the original document score in the
                translated document score attribute.

        """
        if not isinstance(target_lang, (str, list)) or (
            isinstance(target_lang, list)
            and not all(isinstance(lang, str) for lang in target_lang)
        ):
            raise TypeError(
                "`target_lang` must be a string representing a language code "
                "or a list of language codes. "
                "For more information about DeepL supported languages, "
                "see https://developers.deepl.com/docs/resources/supported-languages"
            )

        self.api_key: Secret = api_key
        self.max_retries: int = max_retries
        http_client.max_network_retries = self.max_retries
        self.client: Translator = Translator(auth_key=str(self.api_key.resolve_value()))

        self.source_lang: Optional[str] = source_lang
        self.target_lang: Union[str, List[str]] = target_lang
        self.formality: Formality = Formality(formality or Formality.DEFAULT)
        self.preserve_formatting: bool = preserve_formatting
        self.split_sentences: SplitSentences = SplitSentences(
            split_sentences or SplitSentences.DEFAULT
        )
        self.context: Optional[str] = context
        self.glossary: Union[str, None] = glossary
        self.tag_handling: Literal[None, "xml", "html"] = tag_handling
        self.outline_detection: bool = outline_detection
        self.non_splitting_tags: Union[str, List[str], None] = non_splitting_tags
        self.splitting_tags: Union[str, List[str], None] = splitting_tags
        self.ignore_tags: Union[str, List[str], None] = ignore_tags
        self.include_score: bool = include_score

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
                "DeepLDocumentTranslator expects a list of Haystack documents as input."
            )

        if not documents:
            logger.warning("No documents provided for translation.")
            return {"documents": []}

        target_languages = (
            self.target_lang
            if isinstance(self.target_lang, list)
            else [self.target_lang]
        )

        translated_documents = []

        for target_lang in target_languages:
            translations = self.client.translate_text(
                [doc.content for doc in documents if doc.content],
                source_lang=source_lang or self.source_lang or None,
                target_lang=target_lang,
                formality=self.formality,
            )
            assert isinstance(translations, list)

            for document, translation in zip(documents, translations):
                if document.meta.get("language") or document.meta.get("source_lang"):
                    logger.warning(
                        "Document meta already contains language or source_lang. "
                        "These fields will be overwritten."
                    )

                meta = {
                    **document.meta,
                    "source_lang": translation.detected_source_lang,
                    "language": target_lang,
                }

                translated_documents.append(
                    Document(
                        content=translation.text,
                        meta=meta,
                        score=document.score if self.include_score else None,
                    )
                )

        return {"documents": translated_documents}

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
            preserve_formatting=self.preserve_formatting,
            split_sentences=self.split_sentences.value,
            context=self.context,
            glossary=self.glossary,
            tag_handling=self.tag_handling,
            outline_detection=self.outline_detection,
            non_splitting_tags=self.non_splitting_tags,
            splitting_tags=self.splitting_tags,
            ignore_tags=self.ignore_tags,
            include_score=self.include_score,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeepLDocumentTranslator":
        """Deserializes the component from a dictionary.

        Args:
            data: Dictionary to deserialize from.

        Returns: Deserialized component.

        """
        deserialize_secrets_inplace(data["init_parameters"], keys=["api_key"])
        return default_from_dict(cls, data)
