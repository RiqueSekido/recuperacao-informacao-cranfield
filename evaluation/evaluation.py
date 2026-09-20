"""Métricas de avaliação para rankings de Recuperação de Informação."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class QueryMetrics:
    """Métricas calculadas para uma consulta."""

    precision_at_k: float
    recall_at_k: float
    average_precision: float


@dataclass(frozen=True)
class EvaluationReport:
    """Métricas por consulta e médias agregadas do experimento."""

    per_query: dict[str, QueryMetrics]
    mean_precision_at_k: float
    mean_recall_at_k: float
    mean_average_precision: float


def build_relevance_sets(qrels: Iterable) -> dict[str, set[str]]:
    """Agrupa documentos relevantes por consulta a partir dos qrels.

    A especificação define relevância binária como grau maior ou igual a 1.
    Graus -1 e documentos sem julgamento não entram no conjunto relevante.
    """
    relevant_documents: dict[str, set[str]] = {}

    for qrel in qrels:
        if qrel.relevance >= 1:
            relevant_documents.setdefault(qrel.query_id, set()).add(qrel.doc_id)

    return relevant_documents


def _document_ids(ranking: Sequence) -> list[str]:
    """Aceita resultados do modelo ou uma lista simples de IDs."""
    return [
        result.document_id if hasattr(result, "document_id") else result
        for result in ranking
    ]


def precision_at_k(
    ranking: Sequence,
    relevant_documents: set[str],
    k: int = 10,
) -> float:
    """Calcula a proporção de documentos relevantes nas primeiras k posições."""
    if k <= 0:
        raise ValueError("k deve ser positivo.")

    retrieved_at_k = _document_ids(ranking[:k])
    relevant_retrieved = sum(
        document_id in relevant_documents for document_id in retrieved_at_k
    )
    return relevant_retrieved / k


def recall_at_k(
    ranking: Sequence,
    relevant_documents: set[str],
    k: int = 10,
) -> float:
    """Calcula a fração dos documentos relevantes recuperada nas primeiras k posições."""
    if k <= 0:
        raise ValueError("k deve ser positivo.")
    if not relevant_documents:
        return 0.0

    retrieved_at_k = _document_ids(ranking[:k])
    relevant_retrieved = sum(
        document_id in relevant_documents for document_id in retrieved_at_k
    )
    return relevant_retrieved / len(relevant_documents)


def average_precision(ranking: Sequence, relevant_documents: set[str]) -> float:
    """Calcula AP considerando todas as posições do ranking.

    Cada documento relevante encontrado contribui com a precisão na posição em
    que apareceu. A divisão final usa o total de documentos relevantes nos
    qrels, penalizando itens relevantes que o ranking não recuperou cedo.
    """
    if not relevant_documents:
        return 0.0

    relevant_retrieved = 0
    precision_sum = 0.0

    for position, document_id in enumerate(_document_ids(ranking), start=1):
        if document_id in relevant_documents:
            relevant_retrieved += 1
            precision_sum += relevant_retrieved / position

    return precision_sum / len(relevant_documents)


def evaluate_rankings(
    rankings: Mapping[str, Sequence],
    qrels: Iterable,
    k: int = 10,
) -> EvaluationReport:
    """Calcula Precision@k, Recall@k e MAP para todas as consultas ranqueadas."""
    if k <= 0:
        raise ValueError("k deve ser positivo.")

    relevance_sets = build_relevance_sets(qrels)
    per_query = {}

    for query_id, ranking in rankings.items():
        relevant_documents = relevance_sets.get(query_id, set())
        per_query[query_id] = QueryMetrics(
            precision_at_k=precision_at_k(ranking, relevant_documents, k),
            recall_at_k=recall_at_k(ranking, relevant_documents, k),
            average_precision=average_precision(ranking, relevant_documents),
        )

    if not per_query:
        raise ValueError("É necessário avaliar ao menos uma consulta.")

    total_queries = len(per_query)
    return EvaluationReport(
        per_query=per_query,
        mean_precision_at_k=sum(
            metrics.precision_at_k for metrics in per_query.values()
        )
        / total_queries,
        mean_recall_at_k=sum(
            metrics.recall_at_k for metrics in per_query.values()
        )
        / total_queries,
        mean_average_precision=sum(
            metrics.average_precision for metrics in per_query.values()
        )
        / total_queries,
    )
