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
from reporting.results_export import (
    export_bm25_grid_results,
    export_bm25_grid_rankings,
    export_model_rankings,
    export_model_reports,
    export_query_modification_rankings,
    export_error_candidates,
)
from experiments.bm25_grid import (
    BM25GridResult,
    run_bm25_parameter_grid,
    select_best_preprocessing,
)
from experiments.query_modifications import (
    QUERY_MODIFICATIONS,
    QueryModificationResult,
)
from analysis.error_candidates import select_error_candidates


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
) -> tuple[dict[str, EvaluationReport], dict[str, dict]]:
    """Avalia o modelo vetorial de cada configuração para todas as consultas."""
    print("=" * 70)
    print("AVALIAÇÃO DO MODELO VETORIAL")
    print("=" * 70)

    reports_by_config = {}
    rankings_by_config = {}
    for config in PREPROCESSING_CONFIGS:
        _, processed_queries = processed_by_config[config.name]
        rankings = models_by_config[config.name].rank_all(processed_queries)
        rankings_by_config[config.name] = rankings
        report = evaluate_rankings(rankings, qrels, k=10)
        reports_by_config[config.name] = report

        print(f"Configuração: {config.name}")
        print(f"  Precision@10: {report.mean_precision_at_k:.4f}")
        print(f"  Recall@10:    {report.mean_recall_at_k:.4f}")
        print(f"  MAP:          {report.mean_average_precision:.4f}\n")

    return reports_by_config, rankings_by_config


def build_and_evaluate_bm25_models(
    documents,
    queries,
    processed_by_config,
    qrels,
) -> tuple[
    dict[str, BM25Model],
    dict[str, EvaluationReport],
    dict[str, dict],
]:
    """Executa BM25 padrão em cada configuração e apresenta rankings e métricas."""
    first_query = queries[0]
    titles_by_id = {document.doc_id: document.title for document in documents}
    models_by_config = {}
    reports_by_config = {}
    rankings_by_config = {}

    print("=" * 70)
    print("MODELO PROBABILÍSTICO: BM25 (k1=1.2, b=0.75)")
    print("=" * 70)

    for config in PREPROCESSING_CONFIGS:
        processed_documents, processed_queries = processed_by_config[config.name]
        model = BM25Model(k1=1.2, b=0.75).fit(processed_documents)
        models_by_config[config.name] = model
        ranking = model.rank(processed_queries[first_query.query_id], top_k=10)
        rankings = model.rank_all(processed_queries)
        rankings_by_config[config.name] = rankings
        report = evaluate_rankings(rankings, qrels, k=10)
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

    return models_by_config, reports_by_config, rankings_by_config


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


def run_query_modification_experiment(
    queries,
    processed_by_config,
    vector_models,
    bm25_models,
    standard_bm25_reports,
) -> list[QueryModificationResult]:
    """Executa as cinco reformulações aprovadas nos dois modelos."""
    preprocessing_name = select_best_preprocessing(standard_bm25_reports)
    configuration = next(
        config for config in PREPROCESSING_CONFIGS if config.name == preprocessing_name
    )
    preprocessor = TextPreprocessor(configuration)
    queries_by_id = {query.query_id: query for query in queries}
    _, original_processed_queries = processed_by_config[preprocessing_name]
    experiment_results = []

    for modification in QUERY_MODIFICATIONS:
        if modification.query_id not in queries_by_id:
            raise ValueError(f"Consulta não encontrada: {modification.query_id}")

        original_terms = original_processed_queries[modification.query_id]
        modified_terms = preprocessor.process(modification.modified_text)
        experiment_results.append(
            QueryModificationResult(
                query_id=modification.query_id,
                original_text=queries_by_id[modification.query_id].text,
                modified_text=modification.modified_text,
                strategy=modification.strategy,
                rankings={
                    "original": {
                        "vector": vector_models[preprocessing_name].rank(
                            original_terms,
                            top_k=10,
                        ),
                        "bm25": bm25_models[preprocessing_name].rank(
                            original_terms,
                            top_k=10,
                        ),
                    },
                    "modified": {
                        "vector": vector_models[preprocessing_name].rank(
                            modified_terms,
                            top_k=10,
                        ),
                        "bm25": bm25_models[preprocessing_name].rank(
                            modified_terms,
                            top_k=10,
                        ),
                    },
                },
            )
        )

    return experiment_results


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
    vector_reports, vector_rankings = evaluate_vector_models(
        models_by_config,
        processed_by_config,
        qrels,
    )
    bm25_models, standard_bm25_reports, bm25_rankings = build_and_evaluate_bm25_models(
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
    query_modification_results = run_query_modification_experiment(
        queries,
        processed_by_config,
        models_by_config,
        bm25_models,
        standard_bm25_reports,
    )

    vector_paths = export_model_reports(vector_reports, "vector")
    bm25_paths = export_model_reports(standard_bm25_reports, "bm25")
    vector_ranking_paths = export_model_rankings(
        vector_rankings,
        "vector",
        documents,
        queries,
        qrels,
    )
    bm25_ranking_paths = export_model_rankings(
        bm25_rankings,
        "bm25",
        documents,
        queries,
        qrels,
    )
    grid_summary_path, grid_per_query_path = export_bm25_grid_results(
        bm25_grid_results
    )
    grid_ranking_path = export_bm25_grid_rankings(
        bm25_grid_results,
        documents,
        queries,
        qrels,
    )
    query_modification_path = export_query_modification_rankings(
        query_modification_results,
        documents,
        qrels,
    )
    best_bm25_grid_result = max(
        bm25_grid_results,
        key=lambda result: result.report.mean_average_precision,
    )
    error_candidates = select_error_candidates(
        documents,
        queries,
        qrels,
        best_bm25_grid_result.rankings,
    )
    error_candidates_path = export_error_candidates(
        error_candidates,
        best_bm25_grid_result.preprocessing_name,
        best_bm25_grid_result.k1,
        best_bm25_grid_result.b,
    )
    print("\nResultados exportados em results/")
    for path in (
        *vector_paths,
        *bm25_paths,
        *vector_ranking_paths,
        *bm25_ranking_paths,
        grid_summary_path,
        grid_per_query_path,
        grid_ranking_path,
        query_modification_path,
        error_candidates_path,
    ):
        print(f"  {path}")


if __name__ == "__main__":
    main()
