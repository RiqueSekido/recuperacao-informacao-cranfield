# Guia de implementação: Trabalho 1 de Recuperação da Informação

> Documento de planejamento, não uma implementação concluída. As caixas devem ser marcadas somente após verificar cada entrega.
>
> Fonte principal: `Trabalho_Pratico_1_RI_2026.pdf`, SCC0282, USP/ICMC, professor Marcelo Manzato, 2º semestre de 2026. Enunciado divulgado em 25/08/2026; entrega em **24/09/2026, até 23:59**. Guia elaborado em 19/09/2026 após leitura das quatro páginas.

## 1. Objetivo e como usar este guia

Construir um sistema experimental que recupere documentos da coleção Cranfield com **Modelo Vetorial e BM25**, compare pré-processamentos e parâmetros e explique os resultados com exemplos concretos.

Siga as etapas em ordem. Primeiro obtenha uma execução pequena e verificável; depois execute a matriz experimental completa; por último consolide as análises e o relatório. Mantenha as evidências de cada etapa para que tabelas e conclusões possam ser reproduzidas.

Neste documento:

- **Obrigatório** indica uma exigência do PDF, com sua página.
- **Recomendação** indica uma escolha proposta para este projeto, que pode ser revisada antes dos experimentos finais.
- **Pendente** indica informação ainda ausente ou interpretação que merece confirmação.

O PDF é a especificação acadêmica analisada. Seus comandos sobre entrega e desenvolvimento são registrados como requisitos do projeto; esta tarefa atual consiste apenas em produzir o guia. Nenhum modelo, experimento ou resultado foi implementado ou executado durante sua elaboração.

### Situação inicial

O repositório contém somente `README.md`, com o título do projeto. Ainda não há arquitetura, dependências ou testes estabelecidos. A estrutura abaixo é uma proposta, não uma descrição de arquivos já existentes.

## 2. Mapa dos requisitos e das evidências

| ID | Exigência do enunciado | Evidência esperada | Etapa |
| --- | --- | --- | --- |
| R01 | Cranfield; mesmos documentos, consultas e qrels nos experimentos; qrels exclusivamente para avaliação (p. 1) | Manifesto dos dados, validação de IDs e separação entre recuperação e avaliação | 2, 7 |
| R02 | Tokenização, minúsculas e quatro configurações de stopwords/stemming (pp. 1-2) | Configurações P0-P3, exemplos de tokens e comparação quantitativa | 3, 7 |
| R03 | Modelo Vetorial com ponderação e cosseno (p. 2) | Código, fórmula documentada e teste de score conhecido | 4 |
| R04 | BM25 com cálculo explícito, compreensível e modificável (p. 2) | Função própria de score e teste manual | 5 |
| R05 | Precision@10, Recall@10 e MAP; resultados individuais e agregados (p. 2) | AP por consulta, métricas por consulta e médias | 6, 7 |
| R06 | Comparar modelos com médias, diferenças por consulta e hipóteses (p. 2) | Tabela geral, diferenças de AP e interpretação | 8 |
| R07 | Duas consultas favoráveis ao BM25, duas ao Vetorial e duas ruins para ambos; pelo menos cinco primeiros documentos e relevância em cada caso (p. 2) | Seis fichas com Top-5 de ambos os modelos | 8 |
| R08 | Avaliar k1 em {0.5, 1.2, 2.0} e b em {0, 0.75, 1}; MAP e outra métrica; consulta com mudança perceptível ao variar b (p. 2) | Grade 3 × 3, gráficos e comparação de rankings | 7, 8 |
| R09 | Reformular manualmente cinco consultas; executar originais e versões nos dois modelos e analisar Top-10 (p. 2) | Registro das reformulações e vinte rankings Top-10 | 9 |
| R10 | Investigar pelo menos dois não relevantes nas primeiras posições e um relevante fora do Top-10 (p. 2) | Três fichas de erro com evidências | 10 |
| R11 | Relevante se grau >= 1; -1 e não julgados são não relevantes nas métricas binárias (p. 2) | Regra centralizada e testes de avaliação | 2, 6 |
| R12 | Código, README completo, resultados completos e relatório PDF de até seis páginas (p. 3) | Pacote reproduzível e checklist de entrega | 11 |
| R13 | Declarar uso de IA e compreender código, fórmulas e decisões (p. 3) | Seção de IA e preparação para possível defesa | 11, 12 |

**Prioridade:** a nota aproximada distribui-se em implementação (25%), avaliação e experimentos (20%), análise crítica de consultas/erros (20%), parâmetros/pré-processamento (15%), relatório (10%) e compreensão individual/defesa (10%), conforme p. 4. Reserve tempo para analisar e escrever, além de programar.

## 3. Decisões técnicas propostas

| Assunto | Recomendação | Motivo / limite |
| --- | --- | --- |
| Linguagem | Python; registrar a versão efetivamente usada | Adequado ao processamento textual e à análise experimental |
| Execução | Linha de comando, com configurações em JSON | Permite repetir experimentos e executar uma consulta durante a defesa |
| Interface | Não incluir interface web nesta entrega inicial | O enunciado pede um sistema experimental; não exige frontend, API ou banco |
| Dados | Preferir `ir_datasets` com a coleção `cranfield` | Evita implementar um parser desnecessário e fornece IDs, consultas e julgamentos |
| Texto indexado | Concatenar título e corpo, sem autores e bibliografia | Escolha fixa e explícita; o PDF não determina quais campos usar |
| Pré-processamento | Tokenizador explícito, stopwords em inglês e Porter stemming | Corpus em inglês; manter política idêntica em documentos e consultas |
| Vetorial | TF-IDF e cosseno implementados de forma transparente | Facilita explicar ponderação, normalização e score |
| BM25 | Função própria, com TF, DF, comprimento e média visíveis | Atende à restrição contra implementação pronta que esconda o cálculo |
| Avaliação | Funções próprias pequenas, verificadas com exemplos calculados à mão | Evita depender de defaults incompatíveis com o enunciado |
| Artefatos | CSV para resultados; JSON para configuração e manifesto | Facilita inspeção e reprodução |
| Testes | `unittest` inicialmente; outra ferramenta se justificada | Biblioteca padrão é suficiente para os testes essenciais |

Dependências candidatas: `ir_datasets` para acesso aos dados, `nltk` para stopwords/stemming e `matplotlib` para gráficos. `pandas`, NumPy e scikit-learn são opcionais, caso simplifiquem uma necessidade concreta. **Confirmar com Henrique antes de adicionar dependências de produção**, conforme suas preferências. Nenhuma dependência foi instalada por este guia.

Não incluir Docker, Django, React, embeddings, busca semântica ou expansão automática no escopo inicial. Eles não são necessários para atender aos requisitos identificados.

### Fluxo de dados

```text
documentos -> pré-processamento -> índice e estatísticas -> modelo -> ranking
consultas  -> mesmo pré-processamento ----------------------^

ranking + qrels -> avaliação -> métricas -> tabelas, gráficos e análises
```

O modelo recebe documentos processados e uma consulta. **Não recebe qrels.** A avaliação observa o ranking já produzido, sem alterá-lo. DF, IDF, vocabulário e comprimento médio são calculados apenas a partir dos documentos, nunca das consultas ou dos julgamentos.

### Estrutura sugerida

Criar módulos conforme a etapa precisar deles, evitando arquivos vazios sem função.

```text
cranfield-ir-models/
  README.md
  GUIA_IMPLEMENTACAO.md
  requirements.txt
  .gitignore
  configs/
    experiments.json
    query_variants.json
  src/cranfield_ir/
    __init__.py
    __main__.py           # comandos e argumentos
    data.py               # carregar e validar a coleção
    preprocessing.py
    index.py              # TF, DF, comprimentos e vocabulário
    vector_model.py
    bm25.py
    metrics.py
    experiments.py
    analysis.py           # selecionar casos e exportar evidências
    plots.py
  tests/
    test_data.py
    test_preprocessing.py
    test_models.py
    test_metrics.py
    test_pipeline.py
  data/                   # dados locais; definir política no .gitignore
  results/
    manifest.json
    runs/
    metrics_by_query.csv
    metrics_summary.csv
    analyses/
    figures/
  report/
    relatorio.md          # ou outro formato editável escolhido pelo grupo
    relatorio.pdf
```

Os comandos do README deverão corresponder à estrutura realmente implementada. Não documentar comandos como funcionais antes de testá-los.

## 4. Etapa 1: preparar o projeto e congelar as convenções

- [ ] Identificar integrantes e registrar versão do Python disponível.
- [ ] Confirmar as dependências necessárias e criar ambiente virtual.
- [ ] Definir instruções de instalação e execução, incluindo recursos de linguagem como a lista de stopwords.
- [ ] Criar `.gitignore` para ambiente virtual, caches e arquivos temporários; preservar resultados exigidos na entrega.
- [ ] Registrar escolhas de campos, tokenização, fórmulas, desempate e configurações em um arquivo versionado.
- [ ] Definir um comando para executar uma consulta e outro para executar os experimentos.

**Critério de conclusão:** importar o pacote e executar os testes iniciais a partir de um terminal limpo, usando as instruções do README.

## 5. Etapa 2: carregar e validar a Cranfield

1. Escolher uma única fonte para toda a execução. Preferência: `ir_datasets.load("cranfield")`.
2. Carregar documentos, consultas e qrels em estruturas separadas.
3. Preservar os IDs originais como strings; não substituí-los por posições de listas.
4. Manter título, texto e texto concatenado de recuperação, permitindo exibir documentos nas análises.
5. Construir um mapa de julgamentos por consulta e documento, mantendo o grau original.
6. Centralizar a interpretação binária: `relevant = grade >= 1`; ausência de julgamento implica não relevante para as métricas.
7. Validar IDs únicos, referências dos qrels, textos vazios e julgamentos duplicados/conflitantes. Não corrigir inconsistências silenciosamente.
8. Salvar manifesto com fonte, versão do carregador, contagens, data de obtenção e hash dos dados normalizados.

A documentação consultada de [Cranfield no ir_datasets](https://ir-datasets.com/cranfield.html) informa **1.400 documentos, 225 consultas e 1.837 julgamentos**. Use essas contagens como verificação da fonte escolhida, sem presumir que qualquer arquivo alternativo tenha exatamente a mesma representação. Não misture IDs ou escalas de relevância entre fornecedores.

**Testes:** IDs preservados, associação correta entre consulta e qrel, grau 1 relevante, grau -1 não relevante e documento não julgado não relevante.

**Critério de conclusão:** manifesto validado e uma consulta exibida junto aos IDs de seus documentos relevantes, sem usar essa informação no recuperador.

## 6. Etapa 3: implementar os quatro pré-processamentos

| Código | Tokenização + minúsculas | Remover stopwords | Stemming |
| --- | --- | --- | --- |
| P0 | Sim | Não | Não |
| P1 | Sim | Sim | Não |
| P2 | Sim | Não | Sim |
| P3 | Sim | Sim | Sim |

**Interpretação:** a expressão “sem stopwords e sem stemming” do PDF será tratada como **sem remoção de stopwords e sem stemming**, formando o experimento fatorial esperado. Registrar essa interpretação; confirmar com o professor se houver orientação diferente em aula.

1. Implementar uma função pura `preprocess(text, config) -> list[str]`.
2. Proposta inicial: minúsculas, sequências alfanuméricas como tokens, pontuação/hífens como separadores, preservação de números e sem filtro arbitrário por tamanho. Documentar exemplos para termos científicos com hífen e números.
3. Aplicar remoção de stopwords antes do stemming, quando ambos estiverem ativos.
4. Fixar a lista de stopwords e a versão do stemmer; documentar obtenção dos recursos para execução em outra máquina.
5. Aplicar exatamente a mesma função a documentos e consultas.
6. Construir um índice separado para cada configuração, incluindo TF por documento, DF por termo, comprimento de cada documento e comprimento médio.
7. Exportar estatísticas: vocabulário, total de tokens, comprimento médio e quantidade de documentos/consultas vazios após processamento.

**Atenção:** DF conta documentos que contêm o termo, não o total de ocorrências. O comprimento BM25 conta tokens com repetição, após o pré-processamento, não termos distintos.

**Testes:** transformação de uma frase conhecida em P0-P3; minúsculas; pontuação; repetição; entrada vazia; consulta composta só por stopwords. Não é necessário testar internamente o algoritmo da biblioteca de stemming.

**Critério de conclusão:** tokens e estatísticas reproduzíveis nas quatro configurações, com diferenças explicáveis.

## 7. Etapa 4: implementar o Modelo Vetorial

O modelo representa documento e consulta no mesmo espaço de termos. TF-IDF atribui peso aos termos, e o cosseno compara a direção dos vetores, normalizando suas magnitudes.

**Convenção proposta, não imposta pelo PDF:**

```text
tf_weight(t, x) = 1 + ln(tf(t, x)), se tf(t, x) > 0; senão 0
idf(t) = ln((N + 1) / (df(t) + 1)) + 1
w(t, x) = tf_weight(t, x) * idf(t)
score(q, d) = soma_t[w(t, q) * w(t, d)] / (norma(q) * norma(d))
```

`N` é o número de documentos. Usar a mesma IDF, obtida do corpus, para consulta e documento; incluir todos os termos do documento em sua norma. Termos de consulta fora do vocabulário são ignorados. Norma zero produz score zero, sem divisão por zero.

1. Pré-calcular pesos e normas dos documentos por configuração.
2. Construir o vetor da consulta com o vocabulário do corpus.
3. Calcular o cosseno e ordenar por score decrescente.
4. Desempatar por ID numérico do documento, mantendo o ID original na saída.
5. Retornar ranking completo para avaliação e permitir recortes Top-5/Top-10 na apresentação.
6. Incluir função de explicação com termos compartilhados, TF, IDF, pesos, normas e contribuições ao score.

**Política proposta de ranking:** incluir todos os documentos, inclusive score zero, com desempate determinístico. Assim, uma consulta sem termos conhecidos terá ordem por ID e deverá ser marcada como caso sem evidência lexical. Não interpretar esses empates como sucesso semântico. Aplicar a mesma política ao BM25.

**Testes:** corpus minúsculo com cosseno calculado à mão; consulta vazia; termo desconhecido; empate; vetores proporcionais com cosseno 1. Não comparar apenas com a própria função sendo testada.

**Critério de conclusão:** score manual e implementado concordam dentro de tolerância numérica, e o Top-10 de uma consulta pode ser inspecionado.

## 8. Etapa 5: implementar o BM25 explicitamente

O BM25 combina raridade do termo, frequência com saturação e normalização pelo comprimento do documento.

**Variante proposta:** IDF positiva suavizada e cada termo distinto da consulta contribuindo uma vez. O enunciado não fixa a variante; conferir a fórmula usada em aula antes de congelar os experimentos.

```text
idf_bm25(t) = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
length_factor(d) = 1 - b + b * len(d) / avgdl
contribution(t, d) = idf_bm25(t) * tf(t, d) * (k1 + 1)
                     / (tf(t, d) + k1 * length_factor(d))
score(q, d) = soma das contribuições dos termos distintos de q presentes em d
```

1. Usar TF, DF, `len(d)` e `avgdl` do índice correspondente ao pré-processamento.
2. Ignorar termos ausentes do documento antes da divisão; documento vazio recebe score zero.
3. Se `avgdl == 0`, interromper com erro claro: o corpus processado está vazio.
4. Expor `k1` e `b` na configuração; referência inicial: `k1=1.2`, `b=0.75`.
5. Seguir a mesma política de ranking completo e desempate do Vetorial.
6. Exportar decomposição do score por termo para apoiar a análise de erros e a defesa.

**Conceitos para verificar:** aumentar TF tem ganho decrescente; `k1` controla a saturação; `b=0` desativa a normalização por comprimento e `b=1` a aplica integralmente. Esses efeitos devem ser analisados mantendo as outras condições fixas. Referência conceitual: [capítulo sobre Okapi BM25 do livro Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html), que apresenta variantes; declarar a fórmula exata adotada neste projeto.

**Testes:** score calculado à mão; ausência de termo; empate; efeito de TF mantendo comprimento controlado; com `b=0`, comprimentos diferentes não alteram a contribuição de um termo com mesma TF/IDF; com `b>0`, maior comprimento reduz essa contribuição, mantidas TF e IDF.

**Critério de conclusão:** score reproduzível e explicável sem recorrer a um recuperador BM25 pronto.

## 9. Etapa 6: validar as métricas antes dos experimentos

Para a consulta `q`, sejam `R_q` seus documentos relevantes e `rel_q(i)` um indicador de relevância do documento na posição `i`:

```text
P@10(q) = quantidade de relevantes nas primeiras 10 posições / 10
R@10(q) = quantidade de relevantes nas primeiras 10 posições / |R_q|
P@i(q) = quantidade de relevantes nas primeiras i posições / i
AP(q) = soma_i[P@i(q) * rel_q(i)] / |R_q|
MAP = média de AP(q) sobre todas as consultas avaliadas
```

AP usa o ranking completo; **não substituir MAP por MAP@10**. Por consulta, salvar AP, P@10 e R@10. No agregado, salvar MAP e as médias de P@10 e R@10, com peso igual para cada consulta. Essas distinções seguem a [avaliação de rankings no livro Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html).

Convenções de implementação:

- Se houver menos de dez documentos retornados, o denominador de P@10 continua sendo dez.
- Consulta sem relevantes: adotar AP=0 e Recall@10=0, sinalizar o caso e manter a consulta na média. Verificar se isso ocorre no corpus.
- Não repetir documentos no ranking; validar posições contíguas e IDs válidos.
- Não descartar consultas com desempenho zero ou processadas como vazias.
- Não arredondar os valores antes da agregação; arredondar apenas na apresentação.

**Teste manual essencial:** consulta com três documentos relevantes nas posições 1, 3 e 12. Então `P@10=0.2`, `R@10=2/3` e `AP=(1 + 2/3 + 3/12)/3 = 23/36`. Esse caso detecta o erro de truncar AP no Top-10.

Também testar ranking sem acertos, grau -1, grau 1 e documento não julgado. Métricas extras são opcionais. Se adicionar NDCG@10, declarar a função de ganho e tratar valores negativos/não julgados como zero.

**Critério de conclusão:** testes manuais aprovados antes de confiar em qualquer tabela de resultados.

## 10. Etapa 7: executar a matriz experimental

### Protocolo recomendado

Executar o cruzamento completo simplifica comparações e evita escolher pré-processamento a partir de resultados intermediários:

| Família | Pré-processamentos | Parâmetros | Configurações |
| --- | --- | --- | --- |
| Vetorial | P0, P1, P2, P3 | TF-IDF fixo | 4 |
| BM25 | P0, P1, P2, P3 | k1 ∈ {0.5, 1.2, 2.0} × b ∈ {0, 0.75, 1} | 36 |
| Total | | | **40** |

Com 225 consultas, são **9.000 rankings de consulta** no experimento principal. A matriz completa é uma recomendação de cobertura; o PDF exige as quatro configurações de pré-processamento e os valores de parâmetros, mas não explicita que todos os fatores devam ser cruzados.

1. Fazer um teste integrado em poucas consultas, sem apresentar esse subconjunto como resultado final.
2. Executar as 40 configurações com a mesma coleção e todas as consultas originais.
3. Para comparar pré-processamento, manter o modelo e os parâmetros fixos.
4. Para comparar os modelos, usar o mesmo pré-processamento e BM25 de referência (`1.2`, `0.75`).
5. Para estudar `b`, fixar `k1` e pré-processamento; para estudar `k1`, fixar `b` e pré-processamento.
6. Salvar rankings antes de adicionar anotações de relevância na etapa de avaliação.
7. Gerar tabelas e gráficos diretamente dos arquivos de resultados.

Os qrels permitem avaliar a grade exigida e discutir configurações. Não usar relevância como variável de score, não criar parâmetros por consulta e não promover documentos manualmente. Se destacar a melhor configuração observada, identificá-la como **melhor nesta avaliação**, sem alegar validação em dados independentes.

### Arquivos e contratos de saída

| Arquivo proposto | Conteúdo mínimo |
| --- | --- |
| `manifest.json` | Fonte/hash dos dados, versões, revisão do código e indicação de alterações locais, configurações, fórmulas, desempate e data |
| `runs/<run_id>.csv` | `run_id, query_id, doc_id, rank, score` para o ranking completo |
| `metrics_by_query.csv` | `run_id, query_id, precision_at_10, recall_at_10, ap` |
| `metrics_summary.csv` | `run_id, model, preprocessing, k1, b, query_count, mean_precision_at_10, mean_recall_at_10, map` |
| `analyses/query_cases.csv` | Consulta, categoria, configuração, modelo, posição, documento, score, grau e indicador de relevância |
| `analyses/parameter_case.csv` | Consulta, parâmetros, documentos, posições antes/depois, comprimentos e scores |
| `analyses/query_reformulations.csv` | Texto original/modificado, justificativa, configuração, modelo e mudanças no Top-10 |
| `analyses/error_cases.csv` | Tipo de erro, consulta, documento, posição, julgamento e evidências |

Usar `run_id` único e estável, por exemplo `bm25_p3_k1-1.2_b-0.75`. Arquivos de rankings podem ser comprimidos se necessário; documentar sua leitura. Não versionar caches como substitutos dos resultados exigidos.

**Verificação:** 40 configurações distintas, 225 consultas em cada configuração, 9.000 linhas de métricas individuais e médias recalculáveis a partir delas. Sob a política de ranking completo, cada ranking tem 1.400 documentos únicos. Reexecutar uma configuração e comparar rankings/métricas; timestamps podem mudar.

**Critério de conclusão:** todos os resultados originais completos e rastreáveis, antes da seleção dos exemplos qualitativos.

## 11. Etapa 8: comparar modelos, consultas e parâmetros

### Comparação quantitativa e pré-processamento

- [ ] Tabela P0-P3 × modelos com MAP, média P@10 e média R@10; BM25 de referência fixo.
- [ ] Gráfico de MAP por pré-processamento/modelo.
- [ ] Grade 3 × 3 de MAP e P@10 para BM25, mantendo explícito o pré-processamento.
- [ ] Relacionar mudanças a vocabulário, comprimento, remoção de palavras e agrupamento por stemming.

### Seis consultas obrigatórias

Recomendação: usar P3 e BM25 de referência para a seleção principal, definidos antes de consultar as diferenças. Calcular `delta_AP = AP_BM25 - AP_Vetorial` e usar P@10/R@10 como contexto.

1. Escolher duas consultas com diferença positiva expressiva para BM25.
2. Escolher duas com diferença negativa expressiva para Vetorial.
3. Escolher duas outras consultas em que ambos tenham AP e qualidade do Top-10 baixas.
4. Preferir seis IDs distintos e informar valores concretos que justifiquem “superior” e “insatisfatório”. Não há limiar numérico definido no PDF.

Se uma categoria não aparecer, revisar a correção e examinar as outras comparações previstas, declarando a configuração usada. Se continuar ausente, registrar a evidência e consultar o professor; não fabricar casos nem modificar scores para obtê-los.

Cada ficha deve conter:

- ID, texto original e tokens da consulta.
- Configurações e AP/P@10/R@10 de ambos os modelos.
- **Top-5 de cada modelo**, com posição, ID, título/trecho, score, grau e relevância binária.
- Evidências sobre termos coincidentes, TF, DF/IDF, comprimento, normalização e contribuições ao score.
- Uma hipótese explicativa, distinguindo observação comprovada de interpretação.

Scores BM25 e cosseno têm escalas diferentes: comparar suas posições e métricas, não seus valores absolutos entre modelos.

### Consulta sensível a b

Fixar pré-processamento e `k1=1.2`. Comparar `b=0`, `0.75` e `1` e selecionar uma consulta com entrada/saída ou troca perceptível de posições no Top-10. Mostrar posições, comprimentos e relevância dos documentos afetados. Explicar a mudança pela normalização de comprimento, sem atribuí-la automaticamente a ganho de qualidade.

**Critério de conclusão:** seis fichas completas e uma comparação de `b` que possa ser reproduzida por comando/configuração.

## 12. Etapa 9: reformular manualmente cinco consultas

1. Selecionar cinco consultas e registrar o texto original sem sobrescrevê-lo.
2. Criar uma versão alternativa por consulta: remoção de termo, sinônimo, acréscimo contextual ou ajuste de especificidade.
3. Registrar a justificativa antes de executar a versão modificada. Não copiar termos dos documentos relevantes identificados pelos qrels.
4. Preservar a necessidade de informação sempre que possível. Se ela mudar, explicitar que os qrels originais deixam de representar perfeitamente a nova pergunta.
5. Fixar P3, Vetorial e BM25 de referência, ou declarar outra escolha única para os cinco casos.
6. Executar original e modificada em ambos os modelos: **5 × 2 × 2 = 20 rankings**.
7. Manter esses resultados separados das médias da coleção de consultas originais.

Para cada par de rankings, analisar documentos que entraram/saíram do Top-10, mudanças de posição e quantos relevantes foram recuperados. Pode-se usar interseção dos Top-10 dividida por 10 como medida simples de estabilidade, nomeando sua definição. Se calcular métricas das reformulações, reutilizar os qrels do ID original e registrar a limitação quando houver mudança de intenção.

**Critério de conclusão:** cinco pares de textos, justificativas e Top-10 completos dos dois modelos, incluindo pioras e resultados sem mudança.

## 13. Etapa 10: investigar erros

Selecionar no mínimo dois documentos distintos não relevantes nas primeiras posições e um relevante ausente do Top-10. Recomendação: procurar os não relevantes no Top-5 e identificar a posição efetiva do relevante no ranking completo.

Para cada caso, registrar:

1. Consulta, configuração, documento, posição e julgamento.
2. Título/trecho e termos que contribuíram para o score.
3. Frequência, raridade e comprimento que possam explicar a posição.
4. Possível perda por stopwords/stemming, ausência de sinônimos ou coincidência lexical sem pertinência temática.
5. Conclusão sustentada pela evidência e limitação da interpretação.

Não julgado e explicitamente julgado como -1 valem zero nas métricas, mas devem ser distinguidos na análise. A ausência de julgamento não prova irrelevância temática absoluta. A análise explica o comportamento; não autoriza alterar qrels nem reordenar resultados.

**Critério de conclusão:** três casos documentados, com pelo menos uma inspeção detalhada da decomposição de score.

## 14. Etapa 11: relatório e pacote de entrega

O relatório deve ter **até seis páginas**, em português ou inglês, com as seções exigidas na p. 3. Planejar o espaço desde o início:

| Conteúdo | Espaço aproximado |
| --- | --- |
| Cabeçalho: título, autores, filiação, emails; Introdução | 0,5 página |
| Técnicas Utilizadas: pré-processamento, modelos e fórmulas | 0,75 página |
| Avaliação: dados, qrels, métricas e protocolo | 0,75 página |
| Resultados Obtidos e Análise: comparação, seis consultas, parâmetros, reformulações e erros | 3,5 páginas |
| Considerações finais, Uso de ferramentas de IA e referências | 0,5 página |

Distribuição sugerida, ajustável à legibilidade. Usar tabelas compactas para Top-5 e reformulações; não remover evidências exigidas para economizar espaço. Entregar rankings completos em arquivos suplementares, mantendo os casos e conclusões essenciais no PDF. Não presumir que anexos ou referências estejam fora do limite sem confirmação do professor.

**Uso de ferramentas de IA:** registrar desde já o apoio na análise do enunciado e organização deste plano. Acrescentar programação, depuração ou revisão apenas se essas atividades ocorrerem. O texto final deve refletir o uso real, sem precisar incluir o histórico completo.

### Checklist da entrega

- [ ] Código-fonte completo e configurações utilizadas.
- [ ] README com integrantes, instalação, comandos de execução, versão da linguagem e bibliotecas, identificação e obtenção da base.
- [ ] Recursos externos necessários à execução documentados, inclusive stopwords.
- [ ] Resultados completos, por consulta e agregados, usados nas tabelas e gráficos.
- [ ] Seis consultas analisadas com Top-5 e relevância de ambos os modelos.
- [ ] Grade de parâmetros com MAP e outra métrica; exemplo de alteração de `b`.
- [ ] Cinco reformulações com análise do Top-10 nos dois modelos.
- [ ] Dois não relevantes no topo e um relevante fora do Top-10 investigados.
- [ ] Relatório PDF com todas as seções exigidas e no máximo seis páginas.
- [ ] Seção de IA fiel ao uso real.
- [ ] Execução validada em ambiente limpo seguindo o README.
- [ ] PDF aberto e revisado: fórmulas, acentos, tabelas, gráficos e fontes legíveis.
- [ ] Local/formato de submissão confirmados na disciplina; o PDF não especifica o canal.

## 15. Etapa 12: preparar a possível defesa individual

Cada integrante deve conseguir:

- Seguir uma consulta do texto original até os tokens, pesos, score, ranking e métricas.
- Explicar TF, DF, IDF, cosseno, saturação e normalização por comprimento.
- Calcular um score pequeno e diferenciar AP de MAP e de Precision@10.
- Explicar por que qrels só entram depois da recuperação.
- Prever o efeito de alterar `b`, `k1`, stopwords ou stemming e verificar a previsão.
- Reexecutar um caso e modificar uma configuração sem reconstruir o projeto manualmente.

**Critério de conclusão:** cada integrante reproduz e explica pelo menos uma consulta e um erro usando o código entregue.

## 16. Cronograma sugerido até 24/09

| Data | Entrega do dia | Etapas |
| --- | --- | --- |
| 19/09 | Ambiente, convenções, coleção validada e pré-processamentos | 1-3 |
| 20/09 | Vetorial e BM25 com testes manuais e explicação de score | 4-5 |
| 21/09 | Métricas validadas e matriz experimental completa | 6-7 |
| 22/09 | Comparações, seis consultas e estudo dos parâmetros | 8 |
| 23/09 | Reformulações, erros e primeira versão completa do relatório | 9-11 |
| 24/09 | Revisão do PDF, reprodução em ambiente limpo e submissão antes de 23:59 | 11-12 |

Se o prazo apertar, cortar métricas opcionais, interface e otimizações. Preservar os requisitos obrigatórios e o tempo de análise. Não investir em desempenho antes de medir se a execução da coleção realmente exige isso.

## 17. Pendências e decisões a registrar

Estas informações não impedem a elaboração do guia:

- **Integrantes, filiação e emails:** necessários para README e relatório.
- **Dependências:** confirmar bibliotecas antes de adicioná-las ao projeto.
- **Fórmulas apresentadas em aula:** conferir se há convenção específica de TF-IDF, IDF do BM25 ou peso de frequência na consulta; o PDF não fixa essas variantes.
- **Campos de documento e tokenização:** este guia propõe título + corpo e tokens alfanuméricos; congelar a escolha antes das execuções finais.
- **Formato/canal de envio e eventuais regras adicionais:** consultar o ambiente da disciplina. Não foram informados no PDF.

Registrar mudanças de protocolo com motivo e reexecutar as configurações afetadas. Nunca misturar resultados de versões diferentes sem identificá-las.

## 18. Fontes e limites desta análise

- **Especificação principal:** `Trabalho_Pratico_1_RI_2026.pdf`, localizado originalmente em `C:\Users\henrique-SCDATA\Downloads\Trabalho_Pratico_1_RI_2026.pdf`. Pp. 1-2: metodologia e requisitos; p. 3: IA, entrega e defesa; p. 4: pesos e referências.
- [Cranfield no ir_datasets](https://ir-datasets.com/cranfield.html): estrutura, contagens e campos da coleção.
- [Introduction to Information Retrieval: Okapi BM25](https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html): interpretação dos parâmetros e variantes do modelo.
- [Introduction to Information Retrieval: avaliação de rankings](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html): AP, MAP e avaliação por posições.

As referências externas complementam a explicação; as regras do enunciado prevalecem para este trabalho. As fórmulas e decisões marcadas como propostas não são exigências adicionais do professor. A revisão deste guia verificou a cobertura dos nove requisitos numerados, das regras de relevância e dos entregáveis; a correção do futuro código e dos resultados dependerá dos testes e experimentos previstos acima.
