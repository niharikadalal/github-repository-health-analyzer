from github import Github
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

load_dotenv()

github_client = Github(
    os.getenv("GITHUB_TOKEN")
)


def check_file(repo, path):
    """Check whether a file exists in the repository."""
    try:
        repo.get_contents(path)
        return True
    except Exception:
        return False


def check_directory(repo, path):
    """Check whether a directory exists in the repository."""
    try:
        contents = repo.get_contents(path)
        return isinstance(contents, list)
    except Exception:
        return False


def get_repository_info(repo_name):

    repo = github_client.get_repo(repo_name)

    # -------------------------
    # Basic Statistics
    # -------------------------

    contributors = repo.get_contributors().totalCount
    commits = repo.get_commits().totalCount
    releases = repo.get_releases().totalCount

    # -------------------------
    # Pull Requests
    # -------------------------

    open_prs = repo.get_pulls(
        state="open"
    ).totalCount

    closed_prs = repo.get_pulls(
        state="closed"
    ).totalCount

    merged_prs = 0

    # -------------------------
    # License
    # -------------------------

    try:
        license_name = repo.license.name
    except Exception:
        license_name = "No License"

    # -------------------------
    # Documentation
    # -------------------------

    readme_present = check_file(
        repo,
        "README.md"
    )

    contributing_present = check_file(
        repo,
        "CONTRIBUTING.md"
    )

    docs_present = check_directory(
        repo,
        "docs"
    )

    examples_present = check_directory(
        repo,
        "examples"
    )

    # -------------------------
    # Security / Governance
    # -------------------------

    security_present = check_file(
        repo,
        "SECURITY.md"
    )

    code_of_conduct_present = check_file(
        repo,
        "CODE_OF_CONDUCT.md"
    )

    dependabot_present = check_file(
        repo,
        ".github/dependabot.yml"
    )

    # -------------------------
    # CodeQL
    # -------------------------

    codeql_present = False

    try:

        workflows = repo.get_contents(
            ".github/workflows"
        )

        for workflow in workflows:

            if "codeql" in workflow.name.lower():

                codeql_present = True
                break

    except Exception:

        codeql_present = False

    # -------------------------
    # Repository Age
    # -------------------------

    repo_age_days = (
        datetime.now(timezone.utc)
        - repo.created_at
    ).days

    # -------------------------
    # Last Commit Age
    # -------------------------

    try:

        last_commit = repo.get_commits()[0]

        last_commit_days = (
            datetime.now(timezone.utc)
            - last_commit.commit.author.date
        ).days

    except Exception:

        last_commit_days = None

    # -------------------------
    # Return Data
    # -------------------------

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

        "open_prs": open_prs,

        "closed_prs": closed_prs,

        "merged_prs": merged_prs,

        "license": license_name,

        "created_at": str(
            repo.created_at
        ),

        "updated_at": str(
            repo.updated_at
        ),

        "readme_present": readme_present,

        "contributing_present": contributing_present,

        "security_present": security_present,

        "repo_age_days": repo_age_days,

        "code_of_conduct_present":
            code_of_conduct_present,

        "docs_present": docs_present,

        "examples_present": examples_present,

        "dependabot_present":
            dependabot_present,

        "codeql_present":
            codeql_present,

        "last_commit_days":
            last_commit_days,
    }

    return data