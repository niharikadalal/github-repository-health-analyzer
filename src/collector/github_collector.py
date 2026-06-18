from github import Github
from dotenv import load_dotenv
import os

load_dotenv()

github_client = Github(
    os.getenv("GITHUB_TOKEN")
)

def get_repository_info(repo_name):

    repo = github_client.get_repo(repo_name)

    contributors = repo.get_contributors().totalCount
    commits = repo.get_commits().totalCount
    releases = repo.get_releases().totalCount

    try:
        license_name = repo.license.name
    except:
        license_name = "No License"
    # README Detection
    try:
        repo.get_readme()
        readme_present = True
    except:
        readme_present = False

    # CONTRIBUTING.md Detection
    try:
        repo.get_contents("CONTRIBUTING.md")
        contributing_present = True
    except:
        contributing_present = False

    # SECURITY.md Detection
    try:
        repo.get_contents("SECURITY.md")
        security_present = True
    except:
        security_present = False
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
        "updated_at": str(repo.updated_at),
        "readme_present": readme_present,
        "contributing_present": contributing_present,
        "security_present": security_present
    }

    return data