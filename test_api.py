from src.collector.github_collector import get_repository_info

repo_data = get_repository_info("pallets/flask")

for key, value in repo_data.items():
    print(f"{key}: {value}")