"""Seleção de candidatos para a análise de erros de recuperação."""

from __future__ import annotations

from dataclasses import dataclass

from evaluation.evaluation import build_relevance_sets


@dataclass(frozen=True)
class ErrorCandidate:
    case: str
    query_id: str
    query_text: str
    document_id: str
    document_title: str
    rank: int
    score: float


def select_error_candidates(documents, queries, qrels, rankings) -> list[ErrorCandidate]:
    """Seleciona dois falsos positivos e um relevante fora do Top-10."""
    documents_by_id = {document.doc_id: document for document in documents}
    queries_by_id = {query.query_id: query for query in queries}
    relevant_documents_by_query = build_relevance_sets(qrels)
    false_positive_candidates = []
    missing_relevant_candidates = []

    for query_id, ranking in rankings.items():
        relevant_documents = relevant_documents_by_query.get(query_id, set())
        for rank, result in enumerate(ranking[:10], start=1):
            if result.document_id not in relevant_documents:
                document = documents_by_id[result.document_id]
                false_positive_candidates.append(
                    ErrorCandidate(
                        case="non_relevant_in_top_10",
                        query_id=query_id,
                        query_text=queries_by_id[query_id].text,
                        document_id=result.document_id,
                        document_title=document.title,
                        rank=rank,
                        score=result.score,
                    )
                )

        for rank, result in enumerate(ranking[10:], start=11):
            if result.document_id in relevant_documents:
                document = documents_by_id[result.document_id]
                missing_relevant_candidates.append(
                    ErrorCandidate(
                        case="relevant_outside_top_10",
                        query_id=query_id,
                        query_text=queries_by_id[query_id].text,
                        document_id=result.document_id,
                        document_title=document.title,
                        rank=rank,
                        score=result.score,
                    )
                )
                break

    false_positive_candidates.sort(key=lambda candidate: (candidate.rank, candidate.query_id))
    selected_false_positives = []
    used_query_ids = set()
    for candidate in false_positive_candidates:
        if candidate.query_id not in used_query_ids:
            selected_false_positives.append(candidate)
            used_query_ids.add(candidate.query_id)
        if len(selected_false_positives) == 2:
            break

    if len(selected_false_positives) < 2 or not missing_relevant_candidates:
        raise ValueError("Não foi possível selecionar todos os candidatos de erro.")

    missing_relevant = min(
        missing_relevant_candidates,
        key=lambda candidate: (candidate.rank, candidate.query_id),
    )
    return [*selected_false_positives, missing_relevant]
