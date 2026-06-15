from github import Github

github_client = Github()

def get_repository_info(repo_name):
    repo = github_client.get_repo(repo_name)

    data = {
        "name": repo.name,
        "description": repo.description,
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "watchers": repo.subscribers_count,
        "open_issues": repo.open_issues_count,
        "created_at": str(repo.created_at)
    }

    return data