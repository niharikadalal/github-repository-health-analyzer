from github import Github

github_client = Github()


def get_repository_info(repo_name):

    repo = github_client.get_repo(repo_name)

    contributors = repo.get_contributors().totalCount
    commits = repo.get_commits().totalCount
    releases = repo.get_releases().totalCount

    try:
        license_name = repo.license.name
    except:
        license_name = "No License"

    data = {
        "name": repo.name,
        "description": repo.description,
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "watchers": repo.subscribers_count,
        "open_issues": repo.open_issues_count,
        "contributors": contributors,
        "commits": commits,
        "releases": releases,
        "license": license_name,
        "created_at": str(repo.created_at),
        "updated_at": str(repo.updated_at)
    }

    return data