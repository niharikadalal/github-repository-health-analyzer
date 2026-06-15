from src.collector.github_collector import get_repository_info

repo_data = get_repository_info("pallets/flask")

print(repo_data)