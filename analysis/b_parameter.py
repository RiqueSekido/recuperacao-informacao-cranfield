"""Análise da mudança de ranking causada pelo parâmetro b do BM25."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from reporting.results_export import CSV_DELIMITER, RESULTS_DIRECTORY


@dataclass(frozen=True)
class BVariationCandidate:
    """Consulta cuja ordem de documentos muda ao variar b."""

    preprocessing_name: str
    k1: float
    query_id: str
    difference_score: float
    rankings_at_b_zero: list[dict[str, str]]
    rankings_at_b_one: list[dict[str, str]]


def _ranking_difference(
    ranking_at_b_zero: list[dict[str, str]],
    ranking_at_b_one: list[dict[str, str]],
) -> float:
    """Mede trocas de documentos e mudanças de posição no Top-10."""
    positions_at_b_zero = {
        row["document_id"]: int(row["rank"]) for row in ranking_at_b_zero
    }
    positions_at_b_one = {
        row["document_id"]: int(row["rank"]) for row in ranking_at_b_one
    }
    shared_document_ids = positions_at_b_zero.keys() & positions_at_b_one.keys()
    changed_documents = len(
        positions_at_b_zero.keys() ^ positions_at_b_one.keys()
    )
    position_difference = sum(
        abs(positions_at_b_zero[document_id] - positions_at_b_one[document_id])
        for document_id in shared_document_ids
    )

    return changed_documents + position_difference / 10


def select_b_variation_candidate(
    rankings_path: Path,
) -> BVariationCandidate:
    """Seleciona a maior mudança entre b=0 e b=1 para cada valor de k1."""
    if not rankings_path.exists():
        raise FileNotFoundError(
            f"Ranking da grade não encontrado: {rankings_path}. "
            "Execute: python generate_results.py"
        )

    rankings = {}
    with rankings_path.open(encoding="utf-8") as file:
        for row in csv.DictReader(file, delimiter=CSV_DELIMITER):
            key = (
                row["preprocessing"],
                float(row["k1"]),
                float(row["b"]),
                row["query_id"],
            )
            rankings.setdefault(key, []).append(row)

    for ranking in rankings.values():
        ranking.sort(key=lambda row: int(row["rank"]))

    candidates = []
    preprocessing_names = sorted({key[0] for key in rankings})
    for preprocessing_name in preprocessing_names:
        k1_values = sorted(
            {key[1] for key in rankings if key[0] == preprocessing_name}
        )
        for k1 in k1_values:
            query_ids = {
                query_id
                for current_preprocessing, current_k1, b, query_id in rankings
                if current_preprocessing == preprocessing_name
                and current_k1 == k1
                and b == 0.0
            }
            for query_id in query_ids:
                ranking_at_b_zero = rankings.get(
                    (preprocessing_name, k1, 0.0, query_id)
                )
                ranking_at_b_one = rankings.get(
                    (preprocessing_name, k1, 1.0, query_id)
                )
                if ranking_at_b_zero is None or ranking_at_b_one is None:
                    continue

                candidates.append(
                    BVariationCandidate(
                        preprocessing_name=preprocessing_name,
                        k1=k1,
                        query_id=query_id,
                        difference_score=_ranking_difference(
                            ranking_at_b_zero,
                            ranking_at_b_one,
                        ),
                        rankings_at_b_zero=ranking_at_b_zero,
                        rankings_at_b_one=ranking_at_b_one,
                    )
                )

    if not candidates:
        raise ValueError("Não há rankings comparáveis para b=0 e b=1.")

    return max(candidates, key=lambda candidate: candidate.difference_score)


def _display_ranking(label: str, ranking: list[dict[str, str]]) -> None:
    print(f"  {label}")
    for row in ranking:
        relevance = "relevante" if row["relevant"].lower() == "true" else "não relevante"
        print(
            f"    {row['rank']}. doc={row['document_id']} "
            f"score={float(row['score']):.4f} [{relevance}] | "
            f"{row['document_title']}"
        )


def analyze_b_variation(results_directory: Path = RESULTS_DIRECTORY) -> None:
    """Mostra um caso de mudança perceptível de ranking ao variar b."""
    candidate = select_b_variation_candidate(
        results_directory / "bm25" / "parameter_grid" / "rankings.csv"
    )
    query_text = candidate.rankings_at_b_zero[0]["query_text"]

    print("=" * 70)
    print("EFEITO DO PARÂMETRO b NO RANKING BM25")
    print("=" * 70)
    print(f"Consulta {candidate.query_id}: {query_text}")
    print(f"Pré-processamento: {candidate.preprocessing_name}")
    print(f"k1 fixo: {candidate.k1}")
    print(f"Índice de mudança no Top-10: {candidate.difference_score:.2f}\n")
    _display_ranking("b=0.0 (sem normalização por tamanho)", candidate.rankings_at_b_zero)
    print()
    _display_ranking("b=1.0 (normalização total por tamanho)", candidate.rankings_at_b_one)
