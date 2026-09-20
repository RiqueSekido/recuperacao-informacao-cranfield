# Recuperação de Informação - Cranfield

Este projeto foi desenvolvido para a disciplina de Recuperação de Informação.
O objetivo é comparar um modelo vetorial com TF-IDF e similaridade do cosseno
com o modelo probabilístico BM25 usando a coleção Cranfield.

## Integrantes

- Henrique Yukio Sekido, NUSP 14614564
- Didrick Chancel Lignina Ndombi, NUSP 14822368

## Versão da linguagem e principais bibliotecas utilizadas

- Python 3.9.0
- ir-datasets
- nltk

## Identificação e forma de obtenção da base de dados

Foi utilizada a coleção **Cranfield**, acessada pela biblioteca `ir-datasets`.
A coleção contém documentos científicos, consultas e julgamentos de relevância
(qrels).

## Instruções para instalação das dependências e execução

Com o ambiente virtual ativado, instale as dependências com:

```powershell
python -m pip install -r requirements.txt
```

Para ativar o ambiente virtual no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Execução

O projeto usa um `Makefile` para separar a geração dos resultados da análise.

Para executar todos os experimentos e atualizar os arquivos CSV:

```powershell
make generate
```

Esse comando executa:

- as quatro configurações de pré-processamento;
- o modelo vetorial com TF-IDF e cosseno;
- BM25 com `k1=1.2` e `b=0.75`;
- a grade de parâmetros `k1 ∈ {0.5, 1.2, 2.0}` e `b ∈ {0, 0.75, 1}`;
- as cinco consultas reformuladas;
- a seleção de candidatos para análise comparativa e análise de erros.

Depois de gerar os resultados, os comandos abaixo leem somente os CSVs. Eles
não executam novamente os modelos.

```powershell
make analyze
```

Mostra consultas em que BM25 é superior, o modelo vetorial é superior e em que
os dois modelos apresentam desempenho baixo.

```powershell
make analyze-b
```

Mostra uma consulta em que a mudança de `b` altera o ranking BM25.

```powershell
make analyze-queries
```

Mostra a comparação entre as versões original e modificada das cinco consultas.

```powershell
make analyze-errors
```

Mostra os candidatos usados na análise de erros.

## Organização do projeto

```text
data/              carregamento da coleção Cranfield
preprocessing/     tokenização, stopwords e stemming
models/            modelo vetorial e BM25
evaluation/        Precision@10, Recall@10 e MAP
experiments/       grade BM25 e consultas modificadas
analysis/          seleção de casos para análise
reporting/         exportação dos resultados para CSV
results/           resultados gerados pelos experimentos
```

## Resultados gerados

Os arquivos principais ficam em `results/`:

```text
results/vector/                     métricas e Top-10 do modelo vetorial
results/bm25/preprocessing/         métricas e Top-10 do BM25 padrão
results/bm25/parameter_grid/        resultados da grade de k1 e b
results/query_modifications/        comparação das cinco consultas modificadas
results/error_analysis/             candidatos para a análise de erros
```

Os arquivos `*_metrics.csv` possuem métricas por consulta. Os arquivos
`*_rankings.csv` possuem os documentos retornados, scores e indicação de
relevância.
