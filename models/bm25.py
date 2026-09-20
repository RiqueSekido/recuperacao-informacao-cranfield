"""Modelo probabilístico BM25 com cálculo explícito do score."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import log
from typing import Mapping, Sequence


@dataclass(frozen=True)
class BM25Result:
    """Representa um documento e seu score BM25 para uma consulta."""

    document_id: str
    score: float


class BM25Model:
    """Indexa documentos e produz rankings usando o modelo BM25.

    Para cada termo da consulta, o score usa:

    IDF * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl))

    onde ``tf`` é a frequência do termo no documento, ``dl`` é o tamanho do
    documento e ``avgdl`` é o tamanho médio da coleção.
    """

    def __init__(self, k1: float = 1.2, b: float = 0.75) -> None:
        if k1 < 0:
            raise ValueError("k1 deve ser maior ou igual a zero.")
        if not 0 <= b <= 1:
            raise ValueError("b deve estar entre 0 e 1.")

        self.k1 = k1
        self.b = b
        self._document_ids: list[str] | None = None
        self._document_lengths: dict[str, int] = {}
        self._average_document_length = 0.0
        self._idf: dict[str, float] = {}
        self._postings: dict[str, list[tuple[str, int]]] = {}

    def fit(self, documents: Mapping[str, Sequence[str]]) -> "BM25Model":
        """Calcula IDF, tamanhos e índice invertido dos documentos."""
        if not documents:
            raise ValueError("É necessário fornecer ao menos um documento.")

        self._document_ids = list(documents)
        self._document_lengths = {
            document_id: len(terms) for document_id, terms in documents.items()
        }
        self._average_document_length = (
            sum(self._document_lengths.values()) / len(documents)
        )

        document_frequencies: Counter[str] = Counter()
        postings: defaultdict[str, list[tuple[str, int]]] = defaultdict(list)

        for document_id, terms in documents.items():
            term_frequencies = Counter(terms)
            document_frequencies.update(term_frequencies.keys())

            for term, frequency in term_frequencies.items():
                postings[term].append((document_id, frequency))

        total_documents = len(documents)
        self._idf = {
            term: log(1 + (total_documents - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequencies.items()
        }
        self._postings = dict(postings)
        return self

    def rank(
        self,
        query_terms: Sequence[str],
        top_k: int | None = None,
    ) -> list[BM25Result]:
        """Retorna documentos ordenados pelo score BM25 para uma consulta."""
        if self._document_ids is None:
            raise RuntimeError("O modelo deve executar fit() antes de rank().")
        if top_k is not None and top_k <= 0:
            raise ValueError("top_k deve ser positivo.")

        scores: defaultdict[str, float] = defaultdict(float)
        for term in set(query_terms):
            if term not in self._postings:
                continue

            for document_id, term_frequency in self._postings[term]:
                document_length = self._document_lengths[document_id]
                length_normalization = 1 - self.b + self.b * (
                    document_length / self._average_document_length
                )
                denominator = term_frequency + self.k1 * length_normalization
                term_score = self._idf[term] * (
                    term_frequency * (self.k1 + 1) / denominator
                )
                scores[document_id] += term_score

        results = [
            BM25Result(document_id, scores[document_id])
            for document_id in self._document_ids
        ]
        results.sort(key=lambda result: (-result.score, result.document_id))
        return results if top_k is None else results[:top_k]

    def rank_all(
        self,
        queries: Mapping[str, Sequence[str]],
        top_k: int | None = None,
    ) -> dict[str, list[BM25Result]]:
        """Produz rankings para todas as consultas usando o mesmo índice."""
        return {
            query_id: self.rank(query_terms, top_k)
            for query_id, query_terms in queries.items()
        }
