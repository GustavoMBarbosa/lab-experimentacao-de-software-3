import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==============================
# Configurações iniciais
# ==============================
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (8, 6)

# Caminho do CSV
csv_path = os.path.join("arquivos", "pull_requests.csv")

# Criar pasta de saída para gráficos se não existir
os.makedirs("graficos", exist_ok=True)

# ==============================
# Leitura dos dados
# ==============================
df = pd.read_csv(csv_path)

print(f"Total de PRs carregados: {len(df)}")

# ==============================
# Pré-processamento básico
# ==============================
# Remover valores nulos principais
df = df.dropna(subset=["AnalysisTimeHours", "DescriptionLength", "Reviews", "Additions", "Deletions"])

# Calcular tamanho total dos PRs (adições + deleções)
df["PR_Size"] = df["Additions"] + df["Deletions"]

# Interações totais (comentários + participantes + revisões)
df["Interactions"] = df["Comments"] + df["Participants"] + df["Reviews"]

# ==============================
# A. Feedback Final das Revisões (Status do PR)
# ==============================

# RQ01 - Tamanho vs Feedback (PR_Status)
sns.boxplot(data=df, x="PR_Status", y="PR_Size")
plt.title("RQ01: Relação entre o tamanho dos PRs e o feedback final (Status)")
plt.xlabel("Status do PR (1 = Merged, 0 = Closed)")
plt.ylabel("Tamanho do PR (linhas alteradas)")
plt.tight_layout()
plt.savefig("graficos/RQ01_tamanho_feedback.png")
plt.clf()

# RQ02 - Tempo de análise vs Feedback
sns.boxplot(data=df, x="PR_Status", y="AnalysisTimeHours")
plt.title("RQ02: Relação entre o tempo de análise e o feedback final")
plt.xlabel("Status do PR (1 = Merged, 0 = Closed)")
plt.ylabel("Tempo de Análise (horas)")
plt.tight_layout()
plt.savefig("graficos/RQ02_tempo_feedback.png")
plt.clf()

# RQ03 - Descrição vs Feedback
sns.boxplot(data=df, x="PR_Status", y="DescriptionLength")
plt.title("RQ03: Relação entre a descrição e o feedback final")
plt.xlabel("Status do PR (1 = Merged, 0 = Closed)")
plt.ylabel("Tamanho da descrição (caracteres)")
plt.tight_layout()
plt.savefig("graficos/RQ03_descricao_feedback.png")
plt.clf()

# RQ04 - Interações vs Feedback
sns.boxplot(data=df, x="PR_Status", y="Interactions")
plt.title("RQ04: Relação entre interações e feedback final")
plt.xlabel("Status do PR (1 = Merged, 0 = Closed)")
plt.ylabel("Interações (comentários + participantes + revisões)")
plt.tight_layout()
plt.savefig("graficos/RQ04_interacoes_feedback.png")
plt.clf()

# ==============================
# B. Número de Revisões
# ==============================

# RQ05 - Tamanho vs Revisões
sns.scatterplot(data=df, x="PR_Size", y="Reviews", hue="PR_Status", alpha=0.7)
plt.title("RQ05: Relação entre tamanho e número de revisões")
plt.xlabel("Tamanho do PR (linhas alteradas)")
plt.ylabel("Número de revisões")
plt.tight_layout()
plt.savefig("graficos/RQ05_tamanho_revisoes.png")
plt.clf()

# RQ06 - Tempo vs Revisões
sns.scatterplot(data=df, x="AnalysisTimeHours", y="Reviews", hue="PR_Status", alpha=0.7)
plt.title("RQ06: Relação entre tempo de análise e número de revisões")
plt.xlabel("Tempo de análise (horas)")
plt.ylabel("Número de revisões")
plt.tight_layout()
plt.savefig("graficos/RQ06_tempo_revisoes.png")
plt.clf()

# RQ07 - Descrição vs Revisões
sns.scatterplot(data=df, x="DescriptionLength", y="Reviews", hue="PR_Status", alpha=0.7)
plt.title("RQ07: Relação entre descrição e número de revisões")
plt.xlabel("Tamanho da descrição (caracteres)")
plt.ylabel("Número de revisões")
plt.tight_layout()
plt.savefig("graficos/RQ07_descricao_revisoes.png")
plt.clf()

# RQ08 - Interações vs Revisões
sns.scatterplot(data=df, x="Interactions", y="Reviews", hue="PR_Status", alpha=0.7)
plt.title("RQ08: Relação entre interações e número de revisões")
plt.xlabel("Interações (comentários + participantes + revisões)")
plt.ylabel("Número de revisões")
plt.tight_layout()
plt.savefig("graficos/RQ08_interacoes_revisoes.png")
plt.clf()

print(" Gráficos salvos na pasta 'graficos/' com sucesso!")
