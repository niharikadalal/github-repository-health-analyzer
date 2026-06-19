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


# Read repositories from text file
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

        # Create Label
        if health_score >= 80:
            label = "Healthy"

        elif health_score >= 50:
            label = "Moderately Healthy"

        else:
            label = "At Risk"

        dataset.append({

            "repository": repo_name,

            "stars": repo_data["stars"],
            "forks": repo_data["forks"],
            "watchers": repo_data["watchers"],

            "contributors": repo_data["contributors"],
            "commits": repo_data["commits"],
            "releases": repo_data["releases"],
            "open_issues": repo_data["open_issues"],

            "readme_present": repo_data["readme_present"],
            "contributing_present": repo_data["contributing_present"],
            "security_present": repo_data["security_present"],

            "documentation_score": documentation_score,
            "activity_score": activity_score,
            "community_score": community_score,
            "security_score": security_score,

            "health_score": health_score,
            "label": label
        })

    except Exception as e:

        print(f"Failed: {repo_name}")
        print(e)


df = pd.DataFrame(dataset)

df.to_csv(
    "data/raw/repositories.csv",
    index=False
)

print("\nDataset generated successfully!")
print(f"Total repositories processed: {len(df)}")