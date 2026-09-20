"""Ponto de entrada do projeto de Recuperação de Informação."""

from data.load_cranfield import load_cranfield
from evaluation.evaluation import EvaluationReport, evaluate_rankings
from preprocessing.preprocessing import (
    PREPROCESSING_CONFIGS,
    TextPreprocessor,
    preprocess_collection,
)
from models.vector_model import VectorModel
from models.bm25 import BM25Model
from reporting.results_export import export_bm25_grid_results, export_model_reports
from experiments.bm25_grid import (
    BM25GridResult,
    run_bm25_parameter_grid,
    select_best_preprocessing,
)


def display_processed_samples(
    documents,
    queries,
    processed_by_config,
) -> None:
    """Mostra uma amostra para conferir o efeito das quatro configurações."""
    document = documents[0]
    query = queries[0]

    print("\n" + "=" * 70)
    print("AMOSTRA DO PRÉ-PROCESSAMENTO")
    print("=" * 70)
    print(f"Documento {document.doc_id}: {document.title}")
    print(f"Consulta {query.query_id}: {query.text}\n")

    for config in PREPROCESSING_CONFIGS:
        processed_documents, processed_queries = processed_by_config[config.name]
        document_terms = processed_documents[document.doc_id]
        query_terms = processed_queries[query.query_id]

        print(f"Configuração: {config.name}")
        print(f"  Documento ({len(document_terms)} termos): {document_terms[:20]}")
        print(f"  Consulta ({len(query_terms)} termos): {query_terms}\n")


def build_vector_models_and_display_ranking(
    documents,
    queries,
    processed_by_config,
) -> dict[str, VectorModel]:
    """Cria um modelo vetorial por configuração e mostra um Top-10 real."""
    models_by_config = {}
    first_query = queries[0]
    titles_by_id = {document.doc_id: document.title for document in documents}

    print("=" * 70)
    print("MODELO VETORIAL: TF-IDF + COSSENO")
    print("=" * 70)
    print(f"Consulta usada no exemplo ({first_query.query_id}): {first_query.text}\n")

    for config in PREPROCESSING_CONFIGS:
        processed_documents, processed_queries = processed_by_config[config.name]
        model = VectorModel().fit(processed_documents)
        ranking = model.rank(processed_queries[first_query.query_id], top_k=10)
        models_by_config[config.name] = model

        print(f"Configuração: {config.name}")
        for position, result in enumerate(ranking, start=1):
            title = titles_by_id[result.document_id] or "Sem título"
            print(
                f"  {position:2d}. doc={result.document_id} "
                f"score={result.score:.4f} | {title}"
            )
        print()

    return models_by_config


def evaluate_vector_models(
    models_by_config,
    processed_by_config,
    qrels,
) -> dict[str, EvaluationReport]:
    """Avalia o modelo vetorial de cada configuração para todas as consultas."""
    print("=" * 70)
    print("AVALIAÇÃO DO MODELO VETORIAL")
    print("=" * 70)

    reports_by_config = {}
    for config in PREPROCESSING_CONFIGS:
        _, processed_queries = processed_by_config[config.name]
        rankings = models_by_config[config.name].rank_all(processed_queries)
        report = evaluate_rankings(rankings, qrels, k=10)
        reports_by_config[config.name] = report

        print(f"Configuração: {config.name}")
        print(f"  Precision@10: {report.mean_precision_at_k:.4f}")
        print(f"  Recall@10:    {report.mean_recall_at_k:.4f}")
        print(f"  MAP:          {report.mean_average_precision:.4f}\n")

    return reports_by_config


def build_and_evaluate_bm25_models(
    documents,
    queries,
    processed_by_config,
    qrels,
) -> dict[str, EvaluationReport]:
    """Executa BM25 padrão em cada configuração e apresenta rankings e métricas."""
    first_query = queries[0]
    titles_by_id = {document.doc_id: document.title for document in documents}
    reports_by_config = {}

    print("=" * 70)
    print("MODELO PROBABILÍSTICO: BM25 (k1=1.2, b=0.75)")
    print("=" * 70)

    for config in PREPROCESSING_CONFIGS:
        processed_documents, processed_queries = processed_by_config[config.name]
        model = BM25Model(k1=1.2, b=0.75).fit(processed_documents)
        ranking = model.rank(processed_queries[first_query.query_id], top_k=10)
        report = evaluate_rankings(model.rank_all(processed_queries), qrels, k=10)
        reports_by_config[config.name] = report

        print(f"Configuração: {config.name}")
        for position, result in enumerate(ranking, start=1):
            title = titles_by_id[result.document_id] or "Sem título"
            print(
                f"  {position:2d}. doc={result.document_id} "
                f"score={result.score:.4f} | {title}"
            )
        print(f"  Precision@10: {report.mean_precision_at_k:.4f}")
        print(f"  Recall@10:    {report.mean_recall_at_k:.4f}")
        print(f"  MAP:          {report.mean_average_precision:.4f}\n")

    return reports_by_config


def run_and_display_bm25_parameter_grid(
    processed_by_config,
    qrels,
    standard_bm25_reports,
) -> list[BM25GridResult]:
    """Executa e mostra a grade obrigatória de parâmetros do BM25."""
    preprocessing_name = select_best_preprocessing(standard_bm25_reports)
    processed_documents, processed_queries = processed_by_config[preprocessing_name]
    results = run_bm25_parameter_grid(
        processed_documents,
        processed_queries,
        qrels,
        preprocessing_name,
    )

    print("=" * 70)
    print("GRADE DE PARÂMETROS BM25")
    print("=" * 70)
    print(
        f"Pré-processamento selecionado por MAP: {preprocessing_name} "
        f"(MAP={standard_bm25_reports[preprocessing_name].mean_average_precision:.4f})"
    )
    print("  k1     b     Precision@10  Recall@10    MAP")

    for result in results:
        report = result.report
        print(
            f"  {result.k1:<4.1f}  {result.b:<4.2f}  "
            f"{report.mean_precision_at_k:<12.4f}  "
            f"{report.mean_recall_at_k:<11.4f}  "
            f"{report.mean_average_precision:.4f}"
        )

    return results


def main() -> None:
    documents, queries, qrels = load_cranfield()
    print("Coleção Cranfield carregada com sucesso.")
    print(f"Documentos: {len(documents)}")
    print(f"Consultas: {len(queries)}")
    print(f"Qrels: {len(qrels)}")

    processed_by_config = {}
    for config in PREPROCESSING_CONFIGS:
        preprocessor = TextPreprocessor(config)
        processed_documents, processed_queries = preprocess_collection(
            documents,
            queries,
            preprocessor,
        )
        processed_by_config[config.name] = (
            processed_documents,
            processed_queries,
        )
        print(
            f"Pré-processamento concluído: {config.name} "
            f"({len(processed_documents)} documentos, {len(processed_queries)} consultas)"
        )

    display_processed_samples(documents, queries, processed_by_config)
    models_by_config = build_vector_models_and_display_ranking(
        documents,
        queries,
        processed_by_config,
    )
    vector_reports = evaluate_vector_models(
        models_by_config,
        processed_by_config,
        qrels,
    )
    standard_bm25_reports = build_and_evaluate_bm25_models(
        documents,
        queries,
        processed_by_config,
        qrels,
    )
    bm25_grid_results = run_and_display_bm25_parameter_grid(
        processed_by_config,
        qrels,
        standard_bm25_reports,
    )

    vector_paths = export_model_reports(vector_reports, "vector")
    bm25_paths = export_model_reports(standard_bm25_reports, "bm25")
    grid_summary_path, grid_per_query_path = export_bm25_grid_results(
        bm25_grid_results
    )
    print("\nResultados exportados em results/")
    for path in (*vector_paths, *bm25_paths, grid_summary_path, grid_per_query_path):
        print(f"  {path}")


if __name__ == "__main__":
    main()
