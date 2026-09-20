"""Pré-processamento de textos para a coleção Cranfield.

O corpus Cranfield está em inglês. Por isso, as stopwords e o stemmer desta
implementação são voltados para a língua inglesa.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


ENGLISH_STOPWORDS = frozenset(
    {
        "a", "about", "above", "after", "again", "against", "all", "am",
        "an", "and", "any", "are", "as", "at", "be", "because", "been",
        "before", "being", "below", "between", "both", "but", "by", "can",
        "could", "did", "do", "does", "doing", "down", "during", "each",
        "few", "for", "from", "further", "had", "has", "have", "having",
        "he", "her", "here", "hers", "herself", "him", "himself", "his",
        "how", "i", "if", "in", "into", "is", "it", "its", "itself",
        "just", "me", "more", "most", "my", "myself", "no", "nor", "not",
        "now", "of", "off", "on", "once", "only", "or", "other", "our",
        "ours", "ourselves", "out", "over", "own", "same", "she", "should",
        "so", "some", "such", "than", "that", "the", "their", "theirs",
        "them", "themselves", "then", "there", "these", "they", "this",
        "those", "through", "to", "too", "under", "until", "up", "very",
        "was", "we", "were", "what", "when", "where", "which", "while",
        "who", "whom", "why", "will", "with", "would", "you", "your",
        "yours", "yourself", "yourselves",
    }
)


@dataclass(frozen=True)
class PreprocessingConfig:
    """Define uma das configurações experimentais obrigatórias."""

    name: str
    remove_stopwords: bool
    use_stemming: bool


PREPROCESSING_CONFIGS = (
    PreprocessingConfig("baseline", False, False),
    PreprocessingConfig("without_stopwords", True, False),
    PreprocessingConfig("with_stemming", False, True),
    PreprocessingConfig("without_stopwords_with_stemming", True, True),
)


class TextPreprocessor:
    """Transforma texto bruto em uma sequência de termos normalizados."""

    def __init__(self, config: PreprocessingConfig) -> None:
        self.config = config
        self._stemmer = self._create_stemmer() if config.use_stemming else None

    @staticmethod
    def _create_stemmer():
        """Cria o stemmer somente quando a configuração exige stemming."""
        try:
            from nltk.stem import PorterStemmer
        except ImportError as error:
            raise RuntimeError(
                "Stemming requer NLTK. Instale-o com: pip install nltk"
            ) from error

        return PorterStemmer()

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """Converte para minúsculas e mantém somente termos alfabéticos."""
        return re.findall(r"[a-z]+", text.lower())

    def process(self, text: str) -> list[str]:
        """Aplica tokenização, stopwords e stemming conforme a configuração."""
        tokens = self.tokenize(text)

        if self.config.remove_stopwords:
            tokens = [token for token in tokens if token not in ENGLISH_STOPWORDS]

        if self._stemmer is not None:
            tokens = [self._stemmer.stem(token) for token in tokens]

        return tokens

    def process_many(self, texts: Iterable[str]) -> list[list[str]]:
        """Pré-processa uma coleção de textos usando a mesma configuração."""
        return [self.process(text) for text in texts]


def preprocess_collection(documents, queries, preprocessor: TextPreprocessor):
    """Pré-processa todos os documentos e consultas de uma configuração.

    O título e o texto de cada documento são unidos porque ambos representam
    conteúdo recuperável. Os qrels ficam fora desta etapa e serão usados apenas
    na avaliação dos rankings.
    """
    processed_documents = {
        document.doc_id: preprocessor.process(
            f"{document.title or ''} {document.text or ''}"
        )
        for document in documents
    }
    processed_queries = {
        query.query_id: preprocessor.process(query.text)
        for query in queries
    }

    return processed_documents, processed_queries
