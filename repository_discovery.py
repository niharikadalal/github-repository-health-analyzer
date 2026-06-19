from github import Github, Auth
from dotenv import load_dotenv
import os

load_dotenv()

auth = Auth.Token(
    os.getenv("GITHUB_TOKEN")
)

github_client = Github(auth=auth)

repositories = set()

queries = [

    # =========================
    # HEALTHY REPOSITORIES
    # =========================

    "stars:>50000",

    "topic:machine-learning stars:>10000",

    "topic:cybersecurity stars:>10000",

    "topic:devops stars:>10000",

    "topic:blockchain stars:>10000",

    "topic:web-development stars:>10000",

    # =========================
    # MODERATELY HEALTHY
    # =========================

    "stars:1000..10000",

    "stars:500..5000",

    "topic:data-science stars:500..5000",

    "topic:machine-learning stars:500..5000",

    "topic:cybersecurity stars:500..5000",

    "topic:devops stars:500..5000",

    # =========================
    # AT RISK CANDIDATES
    # =========================

    "stars:<100",

    "stars:<50",

    "stars:<25",

    "stars:<100 forks:<20",

    "stars:<50 forks:<10",

    "stars:<100 pushed:<2024-01-01",

    "stars:<50 pushed:<2024-01-01",

    "topic:machine-learning stars:<100",

    "topic:cybersecurity stars:<100",

    "topic:web-development stars:<100"
]

for query in queries:

    print(f"\nSearching: {query}")

    try:

        results = github_client.search_repositories(
            query=query,
            sort="stars",
            order="desc"
        )

        count = 0

        for repo in results:

            try:

                if repo.archived:
                    continue

                repositories.add(repo.full_name)

                count += 1

                if count >= 10:
                    break

            except:
                continue

    except Exception as e:

        print(f"Error with query '{query}': {e}")

with open("data/repositories.txt", "w") as file:

    for repo in sorted(repositories):
        file.write(repo + "\n")

print("\n===================================")
print(f"Total repositories collected: {len(repositories)}")
print("Saved to data/repositories.txt")
print("===================================")