"""Exibe os candidatos selecionados para a análise de erros."""

import csv
from pathlib import Path

from reporting.results_export import CSV_DELIMITER, RESULTS_DIRECTORY


def main() -> None:
    path = RESULTS_DIRECTORY / "error_analysis" / "candidates.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {path}. Execute: python generate_results.py"
        )

    with path.open(encoding="utf-8") as file:
        candidates = list(csv.DictReader(file, delimiter=CSV_DELIMITER))

    print("=" * 70)
    print("CANDIDATOS PARA ANÁLISE DE ERROS")
    print("=" * 70)
    for candidate in candidates:
        label = (
            "Documento não relevante no Top-10"
            if candidate["case"] == "non_relevant_in_top_10"
            else "Documento relevante fora do Top-10"
        )
        print(label)
        print(f"  Consulta {candidate['query_id']}: {candidate['query_text']}")
        print(
            f"  Documento {candidate['document_id']} na posição "
            f"{candidate['rank']} (score={float(candidate['score']):.4f})"
        )
        print(f"  Título: {candidate['document_title']}")
        print(
            f"  Configuração: {candidate['preprocessing']} | "
            f"k1={candidate['k1']} | b={candidate['b']}\n"
        )


if __name__ == "__main__":
    main()
