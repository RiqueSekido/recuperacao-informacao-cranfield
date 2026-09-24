"""Exibe a comparação Top-10 das cinco consultas reformuladas."""

import csv
from pathlib import Path

from reporting.results_export import CSV_DELIMITER, RESULTS_DIRECTORY


def main() -> None:
    path = RESULTS_DIRECTORY / "query_modifications" / "top10_comparison.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {path}. Execute: python generate_results.py"
        )

    grouped_rows = {}
    with path.open(encoding="utf-8") as file:
        for row in csv.DictReader(file, delimiter=CSV_DELIMITER):
            grouped_rows.setdefault(row["query_id"], []).append(row)

    print("=" * 70)
    print("REFORMULAÇÃO MANUAL DE CONSULTAS")
    print("=" * 70)
    for query_id, rows in grouped_rows.items():
        first_row = rows[0]
        print(f"Consulta {query_id} | Estratégia: {first_row['strategy']}")
        for version in ("original", "modified"):
            version_rows = [row for row in rows if row["version"] == version]
            print(f"  {version}: {version_rows[0]['query_text']}")
            for model_name in ("vector", "bm25"):
                ranking = [row for row in version_rows if row["model"] == model_name]
                relevant_count = sum(
                    row["relevant"].lower() == "true" for row in ranking
                )
                print(f"    {model_name} | relevantes no Top-10: {relevant_count}")
                for row in ranking:
                    relevance = "R" if row["relevant"].lower() == "true" else "-"
                    print(
                        f"      {row['rank']}. [{relevance}] doc={row['document_id']} "
                        f"{row['document_title']}"
                    )
        print()


if __name__ == "__main__":
    main()
