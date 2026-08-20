import joblib
import pandas as pd

from src.collector.github_collector import get_repository_info

from src.scoring.health_score import calculate_health_score

from src.analyzer.documentation_analyzer import calculate_documentation_score
from src.analyzer.activity_analyzer import calculate_activity_score
from src.analyzer.community_analyzer import calculate_community_score
from src.analyzer.security_analyzer import calculate_security_score


# Load trained model
model = joblib.load(
    "models/repository_health_model.pkl"
)


# Get repository
repo_name = input(
    "Enter repository (owner/repo): "
)


# Collect GitHub data
repo_data = get_repository_info(repo_name)


# Calculate scores
documentation_score = calculate_documentation_score(
    repo_data
)

activity_score = calculate_activity_score(
    repo_data
)

community_score = calculate_community_score(
    repo_data
)

security_score = calculate_security_score(
    repo_data
)


# Calculate overall health score
health_score = calculate_health_score(
    documentation_score,
    activity_score,
    community_score,
    security_score
)


# Create ML feature set
features = pd.DataFrame([
    {
        "stars": repo_data["stars"],
        "forks": repo_data["forks"],
        "watchers": repo_data["watchers"],
        "contributors": repo_data["contributors"],
        "commits": repo_data["commits"],
        "releases": repo_data["releases"],
        "open_issues": repo_data["open_issues"],
        "open_prs": repo_data["open_prs"],
        "closed_prs": repo_data["closed_prs"],
        "repo_age_days": repo_data["repo_age_days"],
        "last_commit_days": repo_data["last_commit_days"],

        "documentation_score": documentation_score,
        "activity_score": activity_score,
        "community_score": community_score,
        "security_score": security_score,

        "readme_present": repo_data["readme_present"],
        "contributing_present": repo_data["contributing_present"],
        "docs_present": repo_data["docs_present"],
        "examples_present": repo_data["examples_present"],
        "security_present": repo_data["security_present"],
        "dependabot_present": repo_data["dependabot_present"],
        "codeql_present": repo_data["codeql_present"],
        "code_of_conduct_present":
            repo_data["code_of_conduct_present"]
    }
])


# ML prediction
prediction = model.predict(features)


# Display results
print("\n===================================")
print(" Repository Health Analysis")
print("===================================")

print("\nRepository:", repo_name)

print("\nDocumentation Score:",
      documentation_score)

print("Activity Score:",
      activity_score)

print("Community Score:",
      community_score)

print("Security Score:",
      security_score)

print("\nOverall Health Score:",
      health_score)

print("\nML Prediction:",
      prediction[0])

print("\n===================================")
