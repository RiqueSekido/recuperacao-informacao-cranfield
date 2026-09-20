"""Funções para carregar os dados da coleção Cranfield."""

import ir_datasets


def load_cranfield():
    """Carrega documentos, consultas e qrels do Cranfield.

    Os qrels são retornados para a etapa de avaliação; eles não devem ser
    usados para influenciar o ranking dos modelos.
    """
    dataset = ir_datasets.load("cranfield")

    documents = list(dataset.docs_iter())
    queries = list(dataset.queries_iter())
    qrels = list(dataset.qrels_iter())

    return documents, queries, qrels
