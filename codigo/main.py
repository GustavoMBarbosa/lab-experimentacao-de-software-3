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
        bodyText
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
# Função para buscar PRs
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
            all_prs.extend(prs_page["nodes"])

            if not prs_page["pageInfo"]["hasNextPage"] or len(all_prs) >= max_prs:
                break

            cursor = prs_page["pageInfo"]["endCursor"]
            time.sleep(1)

        except Exception as e:
            print(f"Erro ao buscar PRs de {owner}/{name}: {e}")
            time.sleep(10)

    return all_prs[:max_prs]

# ==============================
# Salvar PRs em CSV
# ==============================
def save_prs_to_csv(prs, filename=CSV_PRS):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "RepoOwner", "RepoName", "PR_Number", "Title", "State",
            "CreatedAt", "ClosedAt", "MergedAt", "AnalysisTimeHours",
            "FilesChanged", "Additions", "Deletions",
            "BodySizeChars", "Participants", "Comments", "Reviews"
        ])

        for pr in prs:
            created_at = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
            closed_at = pr["closedAt"]
            merged_at = pr["mergedAt"]

            end_time = None
            if merged_at:
                end_time = datetime.fromisoformat(merged_at.replace("Z", "+00:00"))
            elif closed_at:
                end_time = datetime.fromisoformat(closed_at.replace("Z", "+00:00"))

            analysis_time = (end_time - created_at).total_seconds() / 3600 if end_time else None

            writer.writerow([
                pr["repo_owner"],
                pr["repo_name"],
                pr["number"],
                pr["title"],
                pr["state"],
                pr["createdAt"],
                pr["closedAt"],
                pr["mergedAt"],
                f"{analysis_time:.2f}" if analysis_time else "",
                pr.get("changedFiles", 0),
                pr.get("additions", 0),
                pr.get("deletions", 0),
                len(pr.get("bodyText", "")) if pr.get("bodyText") else 0,
                pr["participants"]["totalCount"],
                pr["comments"]["totalCount"],
                pr["reviews"]["totalCount"],
            ])

    print(f"Arquivo '{filename}' salvo com sucesso!")

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

    with open(CSV_REPOS, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            owner, name = row["Owner"], row["Name"]
            print(f"Coletando PRs de {owner}/{name}...")
            prs = fetch_pull_requests(owner, name, max_prs=200)

            for pr in prs:
                pr["repo_owner"] = owner
                pr["repo_name"] = name
            prs_dataset.extend(prs)

    print(f"Total de PRs coletados: {len(prs_dataset)}")
    save_prs_to_csv(prs_dataset)

if __name__ == "__main__":
    main()
