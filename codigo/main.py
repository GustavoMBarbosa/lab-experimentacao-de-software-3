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
CSV_OUTPUT = "arquivos/repositorios_populares.csv"

# Query GraphQL para buscar repositórios ordenados por estrelas (qualquer linguagem)
query = """
query ($cursor: String) {
  search(query: "stars:>100", type: REPOSITORY, first: 100, after: $cursor) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ... on Repository {
        name
        url
        owner {
          login
        }
        stargazerCount
        createdAt
      }
    }
  }
}
"""


# ==============================
# Coleta de repositórios
# ==============================
def fetch_repositories(max_repos=200):
    all_repos = []
    cursor = None

    while True:
        try:
            variables = {"cursor": cursor}
            response = requests.post(URL, json={"query": query, "variables": variables}, headers=HEADERS)

            if response.status_code != 200:
                raise Exception(f"Erro {response.status_code} ao buscar dados: {response.text}")

            data = response.json()
            if "errors" in data:
                raise Exception(f"Erro na resposta da API: {data['errors']}")

            repos_page = data["data"]["search"]
            all_repos.extend(repos_page["nodes"])

            print(f"Coletados {len(all_repos)} repositórios até agora...")

            if not repos_page["pageInfo"]["hasNextPage"] or len(all_repos) >= max_repos:
                break

            cursor = repos_page["pageInfo"]["endCursor"]
            time.sleep(1)

        except Exception as e:
            print(f"Erro na requisição: {e}")
            print("Tentando novamente em 10 segundos...")
            time.sleep(10)

    return all_repos[:max_repos]

# ==============================
# Salvar em CSV
# ==============================
def save_to_csv(repos, filename=CSV_OUTPUT):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Owner", "Name", "Stars", "Url", "CreatedAt", "IdadeAnos"])

        now = datetime.now(timezone.utc)

        for r in repos:
            created_at = datetime.fromisoformat(r["createdAt"].replace("Z", "+00:00"))
            idade_meses = (now.year - created_at.year) * 12 + (now.month - created_at.month)
            idade_anos = idade_meses / 12

            writer.writerow([
                r["owner"]["login"],
                r["name"],
                r.get("stargazerCount", 0),
                r["url"],
                r["createdAt"],
                f"{idade_anos:.2f}"
            ])

    print(f"Arquivo '{filename}' salvo com sucesso!")

# ==============================
# Main
# ==============================
def main():
    if not TOKEN:
        print("preencher o TOKEN do GitHub para rodar.")
        return

    print("Iniciando coleta dos 200 repositórios mais populares no GitHub...")
    repos = fetch_repositories(200)
    print(f"Coleta finalizada! Total de repositórios coletados: {len(repos)}")

    print("Salvando dados em CSV...")
    save_to_csv(repos)

if __name__ == "__main__":
    main()
