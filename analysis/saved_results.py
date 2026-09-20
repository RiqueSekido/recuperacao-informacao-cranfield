"""Análise por consulta usando apenas os CSVs já exportados."""

from __future__ import annotations

import csv
from pathlib import Path

from analysis.model_comparison import select_comparison_candidates
from evaluation.evaluation import EvaluationReport, QueryMetrics
from experiments.bm25_grid import select_best_preprocessing
from reporting.results_export import RESULTS_DIRECTORY


def _load_report(metrics_path: Path) -> EvaluationReport:
    """Reconstrói um relatório de avaliação a partir de um CSV por consulta."""
    with metrics_path.open(encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError(f"O arquivo não possui métricas: {metrics_path}")

    per_query = {
        row["query_id"]: QueryMetrics(
            precision_at_k=float(row["precision_at_10"]),
            recall_at_k=float(row["recall_at_10"]),
            average_precision=float(row["average_precision"]),
        )
        for row in rows
    }
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


def _load_reports(directory: Path) -> dict[str, EvaluationReport]:
    """Carrega todos os relatórios de métricas de um modelo."""
    reports = {}
    for metrics_path in directory.glob("*_metrics.csv"):
        configuration = metrics_path.stem.removesuffix("_metrics")
        reports[configuration] = _load_report(metrics_path)

    if not reports:
        raise FileNotFoundError(
            f"Nenhum CSV de métricas encontrado em {directory}. "
            "Execute primeiro: python generate_results.py"
        )

    return reports


def _load_rankings(rankings_path: Path) -> dict[str, list[dict[str, str]]]:
    """Agrupa os rankings CSV pelo identificador da consulta."""
    if not rankings_path.exists():
        raise FileNotFoundError(
            "Ranking não encontrado: "
            f"{rankings_path}. Execute: python generate_results.py"
        )

    rankings_by_query = {}
    with rankings_path.open(encoding="utf-8") as file:
        for row in csv.DictReader(file):
            rankings_by_query.setdefault(row["query_id"], []).append(row)

    for ranking in rankings_by_query.values():
        ranking.sort(key=lambda row: int(row["rank"]))

    return rankings_by_query


def _display_ranking(model_name: str, ranking: list[dict[str, str]]) -> None:
    """Exibe os cinco primeiros documentos já salvos para uma consulta."""
    print(f"    Top-5 {model_name}:")
    for row in ranking[:5]:
        relevance = "relevante" if row["relevant"].lower() == "true" else "não relevante"
        print(
            f"      {row['rank']}. doc={row['document_id']} "
            f"score={float(row['score']):.4f} [{relevance}] | "
            f"{row['document_title']}"
        )


def analyze_saved_results(results_directory: Path = RESULTS_DIRECTORY) -> None:
    """Seleciona e exibe casos comparativos sem recalcular nenhum modelo."""
    vector_directory = results_directory / "vector"
    bm25_directory = results_directory / "bm25" / "preprocessing"
    vector_reports = _load_reports(vector_directory)
    bm25_reports = _load_reports(bm25_directory)
    preprocessing_name = select_best_preprocessing(bm25_reports)

    if preprocessing_name not in vector_reports:
        raise ValueError(
            "O modelo vetorial não possui métricas para o pré-processamento "
            f"{preprocessing_name}."
        )

    candidates_by_group = select_comparison_candidates(
        vector_reports[preprocessing_name],
        bm25_reports[preprocessing_name],
    )
    vector_rankings = _load_rankings(
        vector_directory / f"{preprocessing_name}_rankings.csv"
    )
    bm25_rankings = _load_rankings(
        bm25_directory / f"{preprocessing_name}_rankings.csv"
    )
    group_titles = {
        "bm25_superior": "BM25 superior ao Modelo Vetorial",
        "vector_superior": "Modelo Vetorial superior ao BM25",
        "both_poor": "Desempenho insatisfatório nos dois modelos",
    }

    print("=" * 70)
    print("ANÁLISE COMPARATIVA POR CONSULTA")
    print("=" * 70)
    print(f"Pré-processamento comum: {preprocessing_name}\n")

    for group_name, candidates in candidates_by_group.items():
        print(group_titles[group_name])
        for candidate in candidates:
            query_id = candidate.query_id
            vector_ranking = vector_rankings[query_id]
            bm25_ranking = bm25_rankings[query_id]
            query_text = vector_ranking[0]["query_text"]

            print(f"  Consulta {query_id}: {query_text}")
            print(
                "  AP Vetorial="
                f"{candidate.vector_metrics.average_precision:.4f} | "
                f"AP BM25={candidate.bm25_metrics.average_precision:.4f}"
            )
            _display_ranking("Vetorial", vector_ranking)
            _display_ranking("BM25", bm25_ranking)
        print()
