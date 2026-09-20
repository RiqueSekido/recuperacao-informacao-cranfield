"""Experimentos de variação dos parâmetros do BM25."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from evaluation.evaluation import EvaluationReport, evaluate_rankings
from models.bm25 import BM25Model


K1_VALUES = (0.5, 1.2, 2.0)
B_VALUES = (0.0, 0.75, 1.0)


@dataclass(frozen=True)
class BM25GridResult:
    """Resultado de uma combinação de parâmetros do BM25."""

    preprocessing_name: str
    k1: float
    b: float
    report: EvaluationReport
    rankings: dict[str, list]


def select_best_preprocessing(
    reports_by_config: Mapping[str, EvaluationReport],
) -> str:
    """Seleciona a configuração com maior MAP para a grade de parâmetros.

    Em caso de empate no MAP, Precision@10 e Recall@10 são usados, nessa
    ordem, como critérios de desempate. A função preserva a ordem de entrada
    caso todas as métricas sejam iguais.
    """
    if not reports_by_config:
        raise ValueError("É necessário fornecer relatórios de avaliação.")

    return max(
        reports_by_config,
        key=lambda name: (
            reports_by_config[name].mean_average_precision,
            reports_by_config[name].mean_precision_at_k,
            reports_by_config[name].mean_recall_at_k,
        ),
    )


def run_bm25_parameter_grid(
    processed_documents: Mapping[str, Sequence[str]],
    processed_queries: Mapping[str, Sequence[str]],
    qrels,
    preprocessing_name: str,
) -> list[BM25GridResult]:
    """Avalia todos os pares obrigatórios de k1 e b para uma configuração.

    O mesmo pré-processamento é mantido em toda a grade para que mudanças nas
    métricas possam ser atribuídas aos parâmetros do BM25, e não aos termos
    gerados por outra configuração de pré-processamento.
    """
    results = []

    for k1 in K1_VALUES:
        for b in B_VALUES:
            model = BM25Model(k1=k1, b=b).fit(processed_documents)
            rankings = model.rank_all(processed_queries)
            report = evaluate_rankings(rankings, qrels, k=10)

            results.append(
                BM25GridResult(
                    preprocessing_name=preprocessing_name,
                    k1=k1,
                    b=b,
                    report=report,
                    rankings=rankings,
                )
            )

    return results
