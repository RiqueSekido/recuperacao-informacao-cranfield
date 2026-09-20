"""Modelo vetorial explícito com TF-IDF e similaridade do cosseno."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import log, sqrt
from typing import Mapping, Sequence


@dataclass(frozen=True)
class SearchResult:
    """Representa um documento e seu score para uma consulta."""

    document_id: str
    score: float


class VectorModel:
    """Indexa documentos e produz rankings usando TF-IDF e cosseno.

    TF = 1 + log(frequência do termo no documento)
    IDF = log((N + 1) / (df + 1)) + 1

    A soma suavizada evita divisão por zero. O score final é o produto escalar
    entre consulta e documento dividido pelas normas dos dois vetores.
    """

    def __init__(self) -> None:
        self._document_ids: list[str] | None = None
        self._idf: dict[str, float] = {}
        self._postings: dict[str, list[tuple[str, float]]] = {}
        self._document_norms: dict[str, float] = {}

    @staticmethod
    def _tf_weight(term_frequency: int) -> float:
        """Calcula o peso TF sublinear de um termo."""
        return 1.0 + log(term_frequency)

    def fit(self, documents: Mapping[str, Sequence[str]]) -> "VectorModel":
        """Calcula IDF, vetores TF-IDF e normas dos documentos."""
        if not documents:
            raise ValueError("É necessário fornecer ao menos um documento.")

        self._document_ids = list(documents)
        document_frequencies: Counter[str] = Counter()
        term_frequencies_by_document: dict[str, Counter[str]] = {}

        for document_id, terms in documents.items():
            term_frequencies = Counter(terms)
            term_frequencies_by_document[document_id] = term_frequencies
            document_frequencies.update(term_frequencies.keys())

        total_documents = len(documents)
        self._idf = {
            term: log((total_documents + 1) / (frequency + 1)) + 1
            for term, frequency in document_frequencies.items()
        }

        postings: defaultdict[str, list[tuple[str, float]]] = defaultdict(list)
        self._document_norms = {}

        for document_id, term_frequencies in term_frequencies_by_document.items():
            squared_weights_sum = 0.0

            for term, frequency in term_frequencies.items():
                weight = self._tf_weight(frequency) * self._idf[term]
                postings[term].append((document_id, weight))
                squared_weights_sum += weight**2

            self._document_norms[document_id] = sqrt(squared_weights_sum)

        self._postings = dict(postings)
        return self

    def rank(
        self,
        query_terms: Sequence[str],
        top_k: int | None = None,
    ) -> list[SearchResult]:
        """Retorna documentos ordenados pelo cosseno consulta-documento."""
        if self._document_ids is None:
            raise RuntimeError("O modelo deve executar fit() antes de rank().")
        if top_k is not None and top_k <= 0:
            raise ValueError("top_k deve ser positivo.")

        query_frequencies = Counter(
            term for term in query_terms if term in self._idf
        )
        query_weights = {
            term: self._tf_weight(frequency) * self._idf[term]
            for term, frequency in query_frequencies.items()
        }
        query_norm = sqrt(sum(weight**2 for weight in query_weights.values()))

        dot_products: defaultdict[str, float] = defaultdict(float)
        for term, query_weight in query_weights.items():
            for document_id, document_weight in self._postings[term]:
                dot_products[document_id] += query_weight * document_weight

        results = []
        for document_id in self._document_ids:
            document_norm = self._document_norms[document_id]
            score = 0.0
            if query_norm > 0 and document_norm > 0:
                score = dot_products[document_id] / (query_norm * document_norm)

            results.append(SearchResult(document_id, score))

        results.sort(key=lambda result: (-result.score, result.document_id))
        return results if top_k is None else results[:top_k]

    def rank_all(
        self,
        queries: Mapping[str, Sequence[str]],
        top_k: int | None = None,
    ) -> dict[str, list[SearchResult]]:
        """Produz rankings para todas as consultas usando o mesmo índice."""
        return {
            query_id: self.rank(query_terms, top_k)
            for query_id, query_terms in queries.items()
        }
