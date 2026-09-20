.PHONY: generate analyze analyze-b analyze-queries analyze-errors

generate:
	python generate_results.py

analyze:
	python analyze_results.py

analyze-b:
	python analyze_b_variation.py

analyze-queries:
	python analyze_query_modifications.py

analyze-errors:
	python analyze_errors.py
