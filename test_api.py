from src.collector.github_collector import get_repository_info
from src.analyzer.documentation_analyzer import calculate_documentation_score

repo_data = get_repository_info("pallets/flask")

for key, value in repo_data.items():
    print(f"{key}: {value}")

print()
print(
    "Documentation Score:",
    calculate_documentation_score(repo_data)
)