"""Exportação de métricas experimentais para arquivos CSV."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Mapping

from evaluation.evaluation import EvaluationReport, build_relevance_sets
from experiments.bm25_grid import BM25GridResult


RESULTS_DIRECTORY = Path("results")
MODEL_RESULTS_DIRECTORIES = {
    "vector": RESULTS_DIRECTORY / "vector",
    "bm25": RESULTS_DIRECTORY / "bm25" / "preprocessing",
}
BM25_GRID_DIRECTORY = RESULTS_DIRECTORY / "bm25" / "parameter_grid"
QUERY_MODIFICATIONS_DIRECTORY = RESULTS_DIRECTORY / "query_modifications"
ERROR_ANALYSIS_DIRECTORY = RESULTS_DIRECTORY / "error_analysis"


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


def export_model_rankings(
    rankings_by_config: Mapping[str, Mapping[str, list]],
    model_name: str,
    documents,
    queries,
    qrels,
    results_directory: Path = RESULTS_DIRECTORY,
    top_k: int = 10,
) -> list[Path]:
    """Exporta os Top-k rankings para permitir análise sem recomputar modelos."""
    if top_k <= 0:
        raise ValueError("top_k deve ser positivo.")

    try:
        relative_directory = MODEL_RESULTS_DIRECTORIES[model_name].relative_to(
            RESULTS_DIRECTORY
        )
    except KeyError as error:
        raise ValueError(f"Modelo desconhecido para exportação: {model_name}") from error

    model_results_directory = results_directory / relative_directory
    model_results_directory.mkdir(parents=True, exist_ok=True)
    documents_by_id = {document.doc_id: document for document in documents}
    queries_by_id = {query.query_id: query for query in queries}
    relevant_documents_by_query = build_relevance_sets(qrels)
    output_paths = []

    for configuration, rankings in rankings_by_config.items():
        output_path = model_results_directory / f"{configuration}_rankings.csv"
        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=(
                    "query_id",
                    "query_text",
                    "rank",
                    "document_id",
                    "document_title",
                    "score",
                    "relevant",
                ),
            )
            writer.writeheader()

            for query_id in sorted(rankings):
                relevant_documents = relevant_documents_by_query.get(query_id, set())
                for rank, result in enumerate(rankings[query_id][:top_k], start=1):
                    document = documents_by_id[result.document_id]
                    writer.writerow(
                        {
                            "query_id": query_id,
                            "query_text": queries_by_id[query_id].text,
                            "rank": rank,
                            "document_id": result.document_id,
                            "document_title": document.title,
                            "score": result.score,
                            "relevant": result.document_id in relevant_documents,
                        }
                    )
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


def export_bm25_grid_rankings(
    grid_results: list[BM25GridResult],
    documents,
    queries,
    qrels,
    results_directory: Path = RESULTS_DIRECTORY,
    top_k: int = 10,
) -> Path:
    """Exporta Top-k da grade BM25 para analisar o efeito de b sem recomputar."""
    if top_k <= 0:
        raise ValueError("top_k deve ser positivo.")

    parameter_grid_directory = results_directory / BM25_GRID_DIRECTORY.relative_to(
        RESULTS_DIRECTORY
    )
    parameter_grid_directory.mkdir(parents=True, exist_ok=True)
    output_path = parameter_grid_directory / "rankings.csv"
    documents_by_id = {document.doc_id: document for document in documents}
    queries_by_id = {query.query_id: query for query in queries}
    relevant_documents_by_query = build_relevance_sets(qrels)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=(
                "preprocessing",
                "k1",
                "b",
                "query_id",
                "query_text",
                "rank",
                "document_id",
                "document_title",
                "score",
                "relevant",
            ),
        )
        writer.writeheader()

        for result in grid_results:
            for query_id in sorted(result.rankings):
                relevant_documents = relevant_documents_by_query.get(query_id, set())
                for rank, ranking_result in enumerate(
                    result.rankings[query_id][:top_k],
                    start=1,
                ):
                    document = documents_by_id[ranking_result.document_id]
                    writer.writerow(
                        {
                            "preprocessing": result.preprocessing_name,
                            "k1": result.k1,
                            "b": result.b,
                            "query_id": query_id,
                            "query_text": queries_by_id[query_id].text,
                            "rank": rank,
                            "document_id": ranking_result.document_id,
                            "document_title": document.title,
                            "score": ranking_result.score,
                            "relevant": ranking_result.document_id
                            in relevant_documents,
                        }
                    )

    return output_path


def export_query_modification_rankings(
    experiment_results,
    documents,
    qrels,
    results_directory: Path = RESULTS_DIRECTORY,
) -> Path:
    """Exporta Top-10 original/modificado dos dois modelos para cinco consultas."""
    output_directory = results_directory / QUERY_MODIFICATIONS_DIRECTORY.relative_to(
        RESULTS_DIRECTORY
    )
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / "top10_comparison.csv"
    documents_by_id = {document.doc_id: document for document in documents}
    relevant_documents_by_query = build_relevance_sets(qrels)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=(
                "query_id",
                "strategy",
                "version",
                "query_text",
                "model",
                "rank",
                "document_id",
                "document_title",
                "score",
                "relevant",
            ),
        )
        writer.writeheader()
        for result in experiment_results:
            relevant_documents = relevant_documents_by_query.get(result.query_id, set())
            for version, query_text in (
                ("original", result.original_text),
                ("modified", result.modified_text),
            ):
                for model_name, ranking in result.rankings[version].items():
                    for rank, ranking_result in enumerate(ranking, start=1):
                        document = documents_by_id[ranking_result.document_id]
                        writer.writerow(
                            {
                                "query_id": result.query_id,
                                "strategy": result.strategy,
                                "version": version,
                                "query_text": query_text,
                                "model": model_name,
                                "rank": rank,
                                "document_id": ranking_result.document_id,
                                "document_title": document.title,
                                "score": ranking_result.score,
                                "relevant": ranking_result.document_id
                                in relevant_documents,
                            }
                        )

    return output_path


def export_error_candidates(
    candidates,
    preprocessing_name: str,
    k1: float,
    b: float,
    results_directory: Path = RESULTS_DIRECTORY,
) -> Path:
    """Exporta casos escolhidos para a análise de erros no relatório."""
    output_directory = results_directory / ERROR_ANALYSIS_DIRECTORY.relative_to(
        RESULTS_DIRECTORY
    )
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / "candidates.csv"

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=(
                "case",
                "preprocessing",
                "k1",
                "b",
                "query_id",
                "query_text",
                "document_id",
                "document_title",
                "rank",
                "score",
            ),
        )
        writer.writeheader()
        for candidate in candidates:
            writer.writerow(
                {
                    "case": candidate.case,
                    "preprocessing": preprocessing_name,
                    "k1": k1,
                    "b": b,
                    "query_id": candidate.query_id,
                    "query_text": candidate.query_text,
                    "document_id": candidate.document_id,
                    "document_title": candidate.document_title,
                    "rank": candidate.rank,
                    "score": candidate.score,
                }
            )

    return output_path
