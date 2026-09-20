"""Exportação de métricas experimentais para arquivos CSV."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Mapping

from evaluation.evaluation import EvaluationReport
from experiments.bm25_grid import BM25GridResult


RESULTS_DIRECTORY = Path("results")
MODEL_RESULTS_DIRECTORIES = {
    "vector": RESULTS_DIRECTORY / "vector",
    "bm25": RESULTS_DIRECTORY / "bm25" / "preprocessing",
}
BM25_GRID_DIRECTORY = RESULTS_DIRECTORY / "bm25" / "parameter_grid"


def _write_per_query_metrics(
    output_path: Path,
    report: EvaluationReport,
) -> None:
    """Grava as métricas de cada consulta de um único experimento."""
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=(
                "query_id",
                "precision_at_10",
                "recall_at_10",
                "average_precision",
            ),
        )
        writer.writeheader()

        for query_id in sorted(report.per_query):
            metrics = report.per_query[query_id]
            writer.writerow(
                {
                    "query_id": query_id,
                    "precision_at_10": metrics.precision_at_k,
                    "recall_at_10": metrics.recall_at_k,
                    "average_precision": metrics.average_precision,
                }
            )


def export_model_reports(
    reports_by_config: Mapping[str, EvaluationReport],
    model_name: str,
    results_directory: Path = RESULTS_DIRECTORY,
) -> list[Path]:
    """Exporta um CSV por configuração de pré-processamento de um modelo."""
    try:
        relative_directory = MODEL_RESULTS_DIRECTORIES[model_name].relative_to(
            RESULTS_DIRECTORY
        )
    except KeyError as error:
        raise ValueError(f"Modelo desconhecido para exportação: {model_name}") from error

    model_results_directory = results_directory / relative_directory
    model_results_directory.mkdir(parents=True, exist_ok=True)
    output_paths = []

    for configuration, report in reports_by_config.items():
        output_path = model_results_directory / f"{configuration}_metrics.csv"
        _write_per_query_metrics(output_path, report)
        output_paths.append(output_path)

    return output_paths


def export_bm25_grid_results(
    grid_results: list[BM25GridResult],
    results_directory: Path = RESULTS_DIRECTORY,
) -> tuple[Path, Path]:
    """Exporta métricas agregadas e por consulta da grade de parâmetros BM25."""
    parameter_grid_directory = results_directory / BM25_GRID_DIRECTORY.relative_to(
        RESULTS_DIRECTORY
    )
    parameter_grid_directory.mkdir(parents=True, exist_ok=True)
    aggregate_path = parameter_grid_directory / "summary.csv"
    per_query_path = parameter_grid_directory / "per_query_metrics.csv"

    with aggregate_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=(
                "preprocessing",
                "k1",
                "b",
                "mean_precision_at_10",
                "mean_recall_at_10",
                "map",
            ),
        )
        writer.writeheader()

        for result in grid_results:
            report = result.report
            writer.writerow(
                {
                    "preprocessing": result.preprocessing_name,
                    "k1": result.k1,
                    "b": result.b,
                    "mean_precision_at_10": report.mean_precision_at_k,
                    "mean_recall_at_10": report.mean_recall_at_k,
                    "map": report.mean_average_precision,
                }
            )

    with per_query_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=(
                "preprocessing",
                "k1",
                "b",
                "query_id",
                "precision_at_10",
                "recall_at_10",
                "average_precision",
            ),
        )
        writer.writeheader()

        for result in grid_results:
            for query_id in sorted(result.report.per_query):
                metrics = result.report.per_query[query_id]
                writer.writerow(
                    {
                        "preprocessing": result.preprocessing_name,
                        "k1": result.k1,
                        "b": result.b,
                        "query_id": query_id,
                        "precision_at_10": metrics.precision_at_k,
                        "recall_at_10": metrics.recall_at_k,
                        "average_precision": metrics.average_precision,
                    }
                )

    return aggregate_path, per_query_path
