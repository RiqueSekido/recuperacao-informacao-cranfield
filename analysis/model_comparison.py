"""Seleção de consultas para a análise comparativa entre modelos."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from evaluation.evaluation import EvaluationReport, QueryMetrics


@dataclass(frozen=True)
class ComparisonCandidate:
    """Consulta selecionada para discussão qualitativa entre dois modelos."""

    query_id: str
    vector_metrics: QueryMetrics
    bm25_metrics: QueryMetrics

    @property
    def average_precision_difference(self) -> float:
        """Retorna AP(BM25) menos AP(Modelo Vetorial)."""
        return (
            self.bm25_metrics.average_precision
            - self.vector_metrics.average_precision
        )


def _build_candidate(
    query_id: str,
    vector_report: EvaluationReport,
    bm25_report: EvaluationReport,
) -> ComparisonCandidate:
    return ComparisonCandidate(
        query_id=query_id,
        vector_metrics=vector_report.per_query[query_id],
        bm25_metrics=bm25_report.per_query[query_id],
    )


def select_comparison_candidates(
    vector_report: EvaluationReport,
    bm25_report: EvaluationReport,
    amount_per_group: int = 2,
) -> dict[str, list[ComparisonCandidate]]:
    """Seleciona consultas em que cada modelo vence e em que ambos falham.

    As categorias são disjuntas para evitar que a mesma consulta seja usada em
    mais de uma seção do relatório. Superioridade é medida pela diferença de
    Average Precision; falha conjunta é medida pelo maior AP entre os modelos.
    """
    if amount_per_group <= 0:
        raise ValueError("amount_per_group deve ser positivo.")

    common_query_ids = set(vector_report.per_query) & set(bm25_report.per_query)
    if not common_query_ids:
        raise ValueError("Os relatórios não possuem consultas em comum.")

    candidates = {
        query_id: _build_candidate(query_id, vector_report, bm25_report)
        for query_id in sorted(common_query_ids, reverse=True)
    }
    selected_query_ids: set[str] = set()

    bm25_wins = sorted(
        (
            candidate
            for candidate in candidates.values()
            if candidate.average_precision_difference > 0
        ),
        key=lambda candidate: (
            candidate.average_precision_difference,
            candidate.bm25_metrics.average_precision,
        ),
        reverse=True,
    )[:amount_per_group]
    selected_query_ids.update(candidate.query_id for candidate in bm25_wins)

    vector_wins = sorted(
        (
            candidate
            for candidate in candidates.values()
            if candidate.query_id not in selected_query_ids
            and candidate.average_precision_difference < 0
        ),
        key=lambda candidate: (
            -candidate.average_precision_difference,
            candidate.vector_metrics.average_precision,
        ),
        reverse=True,
    )[:amount_per_group]
    selected_query_ids.update(candidate.query_id for candidate in vector_wins)

    both_poor = sorted(
        (
            candidate
            for candidate in candidates.values()
            if candidate.query_id not in selected_query_ids
        ),
        key=lambda candidate: (
            max(
                candidate.vector_metrics.average_precision,
                candidate.bm25_metrics.average_precision,
            ),
            (
                candidate.vector_metrics.average_precision
                + candidate.bm25_metrics.average_precision
            ),
        ),
    )[:amount_per_group]

    return {
        "bm25_superior": bm25_wins,
        "vector_superior": vector_wins,
        "both_poor": both_poor,
    }
