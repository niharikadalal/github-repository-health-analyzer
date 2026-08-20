import pandas as pd

from src.collector.github_collector import get_repository_info

from src.analyzer.documentation_analyzer import (
    calculate_documentation_score
)

from src.analyzer.activity_analyzer import (
    calculate_activity_score
)

from src.analyzer.community_analyzer import (
    calculate_community_score
)

from src.analyzer.security_analyzer import (
    calculate_security_score
)

from src.scoring.health_score import (
    calculate_health_score
)


# Read repositories
with open("data/repositories.txt", "r") as file:

    repositories = [
        line.strip()
        for line in file.readlines()
        if line.strip()
    ]


dataset = []


for repo_name in repositories:

    try:

        print(f"Processing: {repo_name}")

        repo_data = get_repository_info(repo_name)

        # Calculate scores

        documentation_score = (
            calculate_documentation_score(repo_data)
        )

        activity_score = (
            calculate_activity_score(repo_data)
        )

        community_score = (
            calculate_community_score(repo_data)
        )

        security_score = (
            calculate_security_score(repo_data)
        )

        health_score = (
            calculate_health_score(
                documentation_score,
                activity_score,
                community_score,
                security_score
            )
        )

        # Classification

        if health_score >= 80:

            label = "Healthy"

        elif health_score >= 50:

            label = "Moderately Healthy"

        else:

            label = "At Risk"


        # Store repository data

        dataset.append({

            "repository": repo_name,

            # General repository metrics
            "stars": repo_data["stars"],
            "forks": repo_data["forks"],
            "watchers": repo_data["watchers"],

            # Activity / community
            "contributors": repo_data["contributors"],
            "commits": repo_data["commits"],
            "releases": repo_data["releases"],
            "open_issues": repo_data["open_issues"],
            "open_prs": repo_data["open_prs"],
            "closed_prs": repo_data["closed_prs"],

            # Documentation
            "readme_present":
                repo_data["readme_present"],

            "contributing_present":
                repo_data["contributing_present"],

            "docs_present":
                repo_data["docs_present"],

            "examples_present":
                repo_data["examples_present"],

            # Security / governance
            "security_present":
                repo_data["security_present"],

            "dependabot_present":
                repo_data["dependabot_present"],

            "codeql_present":
                repo_data["codeql_present"],

            "code_of_conduct_present":
                repo_data["code_of_conduct_present"],

            "license":
                repo_data["license"],

            # Time / maturity
            "repo_age_days":
                repo_data["repo_age_days"],

            "last_commit_days":
                repo_data["last_commit_days"],

            # Calculated scores
            "documentation_score":
                documentation_score,

            "activity_score":
                activity_score,

            "community_score":
                community_score,

            "security_score":
                security_score,

            "health_score":
                health_score,

            "label":
                label
        })


    except Exception as e:

        print(f"Failed: {repo_name}")
        print(e)


# Create dataframe

df = pd.DataFrame(dataset)


# Save dataset

df.to_csv(
    "data/raw/repositories.csv",
    index=False
)


# Summary

print("\nDataset generated successfully!")

print(
    f"Total repositories processed: {len(df)}"
)

print("\nLabel distribution:")

print(
    df["label"].value_counts()
)

print("\nColumns:")

print(
    df.columns.tolist()
)