import pandas as pd
import os

# ==============================
# Configurações
# ==============================
CSV_INPUT = "arquivos/pull_requests.csv"     # dataset completo gerado na sprint 1
CSV_OUTPUT = "arquivos/resumo_medianas.csv"  # arquivo de saída com as medianas

# ==============================
# Função para calcular medianas
# ==============================
def calcular_medianas(csv_entrada=CSV_INPUT, csv_saida=CSV_OUTPUT):
    if not os.path.exists(csv_entrada):
        print(f"Arquivo '{csv_entrada}' não encontrado.")
        return

    # Ler dataset de PRs
    df = pd.read_csv(csv_entrada)

    # Garantir nomes de colunas consistentes (tolerar variações)
    df.columns = [col.strip() for col in df.columns]

    # Selecionar as métricas principais conforme o enunciado
    colunas_metricas = {
        "Tamanho (Arquivos Modificados)": "FilesChanged",
        "Linhas Adicionadas": "Additions",
        "Linhas Removidas": "Deletions",
        "Total de Linhas Alteradas": "TotalLinesChanged" if "TotalLinesChanged" in df.columns else None,
        "Tempo de Análise (h)": "AnalysisTimeHours",
        "Tamanho da Descrição (caracteres)": "DescriptionLength",
        "Participantes": "Participants",
        "Comentários": "Comments",
        "Revisões": "Reviews"
    }

    # Filtrar apenas colunas que existem
    colunas_existentes = {k: v for k, v in colunas_metricas.items() if v in df.columns}

    # Calcular medianas
    medianas = {}
    for nome, coluna in colunas_existentes.items():
        medianas[nome] = round(df[coluna].median(), 2)

    # Criar DataFrame de resumo
    resumo_df = pd.DataFrame(list(medianas.items()), columns=["Métrica", "Mediana"])

    # Salvar em CSV
    os.makedirs(os.path.dirname(csv_saida), exist_ok=True)
    resumo_df.to_csv(csv_saida, index=False, encoding="utf-8")

    print(f"Resumo de medianas salvo em '{csv_saida}' com sucesso!")
    print(resumo_df)

# ==============================
# Execução principal
# ==============================
if __name__ == "__main__":
    calcular_medianas()
