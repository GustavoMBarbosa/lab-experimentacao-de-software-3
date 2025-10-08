import requests
import csv
import time
import os
from datetime import datetime, timezone

# ==============================
# Configurações
# ==============================
TOKEN = ""  # coloque aqui seu token do GitHub
URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
CSV_REPOS = "arquivos/repositorios_populares.csv"
CSV_PRS = "arquivos/pull_requests.csv"

# ==============================
# Query GraphQL para contar PRs de um repositório
# ==============================
query_pr_count = """
query ($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    pullRequests(states: [MERGED, CLOSED]) {
      totalCount
    }
  }
}
"""

# ==============================
# Query GraphQL para buscar PRs
# ==============================
query_prs = """
query ($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(first: 50, after: $cursor, states: [MERGED, CLOSED], orderBy: {field: CREATED_AT, direction: DESC}) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        number
        title
        body
        createdAt
        closedAt
        mergedAt
        additions
        deletions
        changedFiles
        participants {
          totalCount
        }
        comments {
          totalCount
        }
        reviews {
          totalCount
        }
        state
      }
    }
  }
}
"""

# ==============================
# Função para checar se repo tem >= 100 PRs
# ==============================
def has_enough_prs(owner, name, min_prs=100):
    try:
        variables = {"owner": owner, "name": name}
        response = requests.post(URL, json={"query": query_pr_count, "variables": variables}, headers=HEADERS)

        if response.status_code != 200:
            print(f"Erro {response.status_code} ao checar PRs de {owner}/{name}")
            return False

        data = response.json()
        repo = data["data"]["repository"]
        if not repo:
            return False

        total_prs = repo["pullRequests"]["totalCount"]
        return total_prs >= min_prs

    except Exception as e:
        print(f"Erro ao verificar PRs de {owner}/{name}: {e}")
        return False

# ==============================
# Função para buscar PRs (com filtros)
# ==============================
# ==============================
# Função para buscar PRs (com filtros e métricas completas)
# ==============================
def fetch_pull_requests(owner, name, max_prs=200):
    all_prs = []
    cursor = None

    while True:
        try:
            variables = {"owner": owner, "name": name, "cursor": cursor}
            response = requests.post(URL, json={"query": query_prs, "variables": variables}, headers=HEADERS)

            if response.status_code != 200:
                raise Exception(f"Erro {response.status_code} ao buscar PRs: {response.text}")

            data = response.json()
            if "errors" in data:
                raise Exception(f"Erro na resposta da API: {data['errors']}")

            repo = data["data"]["repository"]
            if not repo:
                break

            prs_page = repo["pullRequests"]

            for pr in prs_page["nodes"]:
                # Filtro: pelo menos uma revisão
                if pr.get("reviews", {}).get("totalCount", 0) < 1:
                    continue

                # Tempo de análise
                created_at = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
                end_time = None
                if pr.get("mergedAt"):
                    end_time = datetime.fromisoformat(pr["mergedAt"].replace("Z", "+00:00"))
                elif pr.get("closedAt"):
                    end_time = datetime.fromisoformat(pr["closedAt"].replace("Z", "+00:00"))

                if not end_time:
                    continue

                analysis_time = (end_time - created_at).total_seconds() / 3600

                # Garantir valores default
                additions = pr.get("additions") or 0
                deletions = pr.get("deletions") or 0
                changed_files = pr.get("changedFiles") or 0
                body_length = len(pr.get("body") or "")

                # Métrica derivada opcional
                lines_per_file = (additions + deletions) / changed_files if changed_files > 0 else 0

                # Status binário
                pr_status = 1 if pr["state"] == "MERGED" else 0

                # Adicionar métricas
                pr.update({
                    "analysis_time_hours": analysis_time,
                    "description_length": body_length,
                    "total_lines_changed": additions + deletions,
                    "additions": additions,
                    "deletions": deletions,
                    "changedFiles": changed_files,
                    "lines_per_file": lines_per_file,
                    "pr_status": pr_status
                })

                all_prs.append(pr)

            if not prs_page["pageInfo"]["hasNextPage"] or len(all_prs) >= max_prs:
                break

            cursor = prs_page["pageInfo"]["endCursor"]
            time.sleep(1)

        except Exception as e:
            print(f"Erro ao buscar PRs de {owner}/{name}: {e}")
            print(f"tentando novamente em 10 segundos...")
            time.sleep(10)

    return all_prs[:max_prs]

# ==============================
# Salvar PRs em CSV (com métricas completas)
# ==============================
def save_prs_to_csv(prs, filename=CSV_PRS):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "RepoOwner", "RepoName", "PR_Number", "Title", "State",
            "PR_Status", "CreatedAt", "ClosedAt", "MergedAt", "AnalysisTimeHours",
            "FilesChanged", "Additions", "Deletions", "TotalLinesChanged",
            "LinesPerFile", "DescriptionLength", "Participants", "Comments", "Reviews"
        ])

        for pr in prs:
            writer.writerow([
                pr["repo_owner"],
                pr["repo_name"],
                pr["number"],
                pr["title"],
                pr["state"],
                pr.get("pr_status", 0),
                pr["createdAt"],
                pr.get("closedAt"),
                pr.get("mergedAt"),
                f"{pr.get('analysis_time_hours', 0):.2f}",
                pr.get("changedFiles", 0),
                pr.get("additions", 0),
                pr.get("deletions", 0),
                pr.get("total_lines_changed", 0),
                f"{pr.get('lines_per_file', 0):.2f}",
                pr.get("description_length", 0),
                pr.get("participants", {}).get("totalCount", 0),
                pr.get("comments", {}).get("totalCount", 0),
                pr.get("reviews", {}).get("totalCount", 0),
            ])

    print(f"Arquivo '{filename}' salvo com {len(prs)} PRs válidos!")

# ==============================
# Main
# ==============================
def main():
    if not TOKEN:
        print("Preencha o TOKEN do GitHub para rodar.")
        return

    if not os.path.exists(CSV_REPOS):
        print("Arquivo de repositórios não encontrado. Rode antes a coleta de repositórios.")
        return

    prs_dataset = []
    total_repos = 0

    with open(CSV_REPOS, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        repos_list = list(reader)
        total_repos = len(repos_list)

        for i, row in enumerate(repos_list):
            owner, name = row["Owner"], row["Name"]

            # Só processa repositórios com >= 100 PRs MERGED+CLOSED
            if not has_enough_prs(owner, name):
                print(f"Pulando {owner}/{name} (menos de 100 PRs MERGED+CLOSED)")
                continue

            print(f"Coletando PRs de {owner}/{name} ({i+1}/{total_repos})...")

            prs = fetch_pull_requests(owner, name, max_prs=200)

            for pr in prs:
                pr["repo_owner"] = owner
                pr["repo_name"] = name
                prs_dataset.append(pr)

            time.sleep(2)  # evitar rate limit

    print(f"Coleta finalizada! Total de PRs válidos: {len(prs_dataset)}")
    save_prs_to_csv(prs_dataset)

if __name__ == "__main__":
    main()
