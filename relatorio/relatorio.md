# 🧪 Laboratório 03 - Caracterizando a Atividade de Code Review no GitHub

## 1. Informações do grupo
- **🎓 Curso:** Engenharia de Software  
- **📘 Disciplina:** Laboratório de Experimentação de Software  
- **🗓 Período:** 6° Período  
- **👨‍🏫 Professor:** Danilo de Quadros Maia Filho  
- **👥 Membros do Grupo:** Gabriel Henrique Silva Pereira e Gustavo Menezes Barbosa

---

## 2. Introdução
O objetivo deste laboratório é analisar a atividade de code review em repositórios populares do GitHub, observando como características de Pull Requests (PRs) — como tamanho, tempo de análise, descrição e interações — influenciam o resultado final do processo de revisão (merge ou fechamento).

Essa análise visa compreender fatores que podem impactar a aceitação de contribuições em projetos open-source, fornecendo evidências sobre práticas de colaboração, revisão e engajamento.

### 2.1 Questões de Pesquisa (Research Questions – RQs)

| RQ | Pergunta |
|----|-----------|
| RQ01 | Qual a relação entre o tamanho dos PRs e o feedback final das revisões? |
| RQ02 | Qual a relação entre o tempo de análise dos PRs e o feedback final das revisões? |
| RQ03 | Qual a relação entre a descrição dos PRs e o feedback final das revisões? |
| RQ04 | Qual a relação entre as interações nos PRs e o feedback final das revisões? |
| RQ05 | Qual a relação entre o tamanho dos PRs e o número de revisões realizadas? |
| RQ06 | Qual a relação entre o tempo de análise dos PRs e o número de revisões realizadas? |
| RQ07 | Qual a relação entre a descrição dos PRs e o número de revisões realizadas? |
| RQ08 | Qual a relação entre as interações nos PRs e o número de revisões realizadas? |

---

### 2.2 Hipóteses Informais (Informal Hypotheses – IH)

| IH | Descrição |
|----|------------|
| IH01 | PRs maiores (com mais arquivos e linhas alteradas) tendem a levar mais tempo para serem revisados. |
| IH02 | PRs com descrições mais detalhadas têm maior probabilidade de serem aceitos (MERGED). |
| IH03 | PRs com maior número de participantes e comentários representam revisões mais colaborativas e complexas. |
| IH04 | PRs analisados rapidamente (menos de 24h) tendem a ser menores e mais simples. |
| IH05 | Projetos populares, com muitos PRs, apresentam padrões mais consistentes de revisão e aceitação. |

---

## 3. Tecnologias e ferramentas utilizadas
- **💻 Linguagem de Programação:** Python
- **🛠 Bibliotecas:** `requests`, `csv`, `time`, `os`, `datetime`, `timezone`
- **🌐 API Utilizada:** GitHub GraphQL API
- **📦 Dependências:** apenas bibliotecas nativas do Python + `requests`

---

## 4. Metodologia

### 4.1 Coleta de dados
A coleta foi realizada através da GitHub GraphQL API, utilizando scripts em Python.  
Foram coletados dados de 200 repositórios populares (ordenados por número de estrelas), com o objetivo de identificar padrões de code review em projetos amplamente utilizados.

De cada repositório foram extraídos:
- Pull Requests com status MERGED ou CLOSED;  
- Somente repositórios com ≥100 PRs válidos;  
- PRs contendo pelo menos uma revisão (reviewCount ≥ 1).

---

### 4.2 Filtragem e paginação
Devido ao limite de requisições da API, foi utilizada paginação para coletar 50 PRs por página.  
Foram aplicados filtros adicionais:
- Exclusão de PRs com menos de 1 hora de análise (criação → merge/close).  
- Apenas PRs com revisões humanas (evitando automações de CI/CD).  
- Controle de taxa de requisição com `time.sleep()` para evitar bloqueio da API.

---

### 4.3 Pré-processamento e normalização
Os dados coletados foram processados em CSV, resultando nos seguintes campos principais:
- **RepoOwner / RepoName** → identificação do projeto.  
- **State / PR_Status** → indica se o PR foi aceito (MERGED=1) ou fechado sem merge (CLOSED=0).  
- **AnalysisTimeHours** → tempo total de análise em horas.  
- **FilesChanged, Additions, Deletions, TotalLinesChanged** → medidas de tamanho.  
- **DescriptionLength** → número de caracteres da descrição do PR.  
- **Participants, Comments, Reviews** → métricas de interação.

---

### 4.4 Métricas consideradas

| Código | Métrica | Descrição |
|--------|----------|------------|
| M01 | 🧾 Tamanho (arquivos, linhas adicionadas/removidas) | Mede a extensão do PR. |
| M02 | ⏱ Tempo de Análise (horas) | Intervalo entre criação e fechamento/merge do PR. |
| M03 | 📝 Descrição (nº de caracteres) | Tamanho da descrição fornecida pelo autor. |
| M04 | 💬 Interações | Número de participantes, comentários e revisões. |
| M05 | ✅ Status Final | Indica se o PR foi aceito (MERGED) ou rejeitado (CLOSED). |

---

### 4.5 Cálculo de métricas e geração de dataset
Cada PR coletado foi transformado em uma linha no dataset `pull_requests.csv`.  
Posteriormente, foi criado um resumo estatístico (`resumo_medianas.csv`) contendo as medianas das métricas principais:

| Métrica | Mediana |
|----------|----------|
| Tamanho (Arquivos Modificados) | 3.0 |
| Linhas Adicionadas | 45.0 |
| Linhas Removidas | 20.0 |
| Total de Linhas Alteradas | 65.0 |
| Tempo de Análise (h) | 12.5 |
| Tamanho da Descrição (caracteres) | 220.0 |
| Participantes | 2.0 |
| Comentários | 3.0 |
| Revisões | 1.0 |

---

## 5. Resultados Iniciais (Sprint 2)

### 5.1 Observações gerais
Os resultados iniciais mostram que:
- A maioria dos PRs possui até 3 arquivos modificados, indicando granularidade adequada.  
- O tempo mediano de análise é de aproximadamente 12 horas, sugerindo revisões rápidas em muitos casos.  
- O número mediano de revisões é 1, mostrando que a maioria das contribuições passa por uma única iteração de review.  
- A descrição dos PRs apresenta variação significativa — alguns PRs têm descrições muito curtas, o que pode impactar negativamente a aceitação.  
- PRs com mais comentários tendem a ter tempos de análise maiores.

---

### 5.2 Relação com as hipóteses iniciais

| Hipótese | Status | Observação |
|-----------|---------|------------|
| IH01 – PRs maiores demoram mais | Parcialmente confirmada | PRs extensos tendem a ter tempo maior de análise. |
| IH02 – PRs com boas descrições são mais aceitos | Ainda em análise | Requer correlação entre descrição e status final. |
| IH03 – PRs com mais interações são mais complexos | Confirmada | Revisões com muitos comentários envolvem mais participantes. |
| IH04 – Revisões rápidas são de PRs simples | Confirmada | PRs com poucas linhas alteradas têm tempos curtos. |
| IH05 – Repositórios populares apresentam consistência | Confirmada | Repositórios grandes mantêm padrão de revisão similar. |

---

## 6. Conclusão Parcial

Até o momento (Sprint 2), foram obtidos:
- Um dataset consistente e filtrado de Pull Requests (MERGED/CLOSED com revisões válidas).
- Cálculo das principais métricas e medianas descritivas.
- Formulação e verificação inicial das hipóteses informais.

As próximas etapas (Sprint 3) envolverão:
- Geração de gráficos (histogramas, boxplots e heatmaps).
- Discussão aprofundada sobre relações entre tamanho, tempo e feedback final das revisões.

---

## 7. Referências
- [📘 GitHub GraphQL API Documentation](https://docs.github.com/en/graphql)
- [📙 Python Requests Library](https://requests.readthedocs.io/en/latest/)
- [📙 Python CSV Module](https://docs.python.org/3/library/csv.html)
- [📘 Documentação do módulo datetime](https://docs.python.org/3/library/datetime.html)
- [📘 Template de relatório](https://github.com/joaopauloaramuni/laboratorio-de-experimentacao-de-software/blob/main/TEMPLATES/template_report.md)
---
