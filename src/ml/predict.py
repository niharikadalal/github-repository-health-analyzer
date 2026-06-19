import joblib
import pandas as pd
from src.collector.github_collector import get_repository_info
from src.scoring.health_score import calculate_health_score
from src.analyzer.documentation_analyzer import calculate_documentation_score
from src.analyzer.activity_analyzer import calculate_activity_score
from src.analyzer.community_analyzer import calculate_community_score
from src.analyzer.security_analyzer import calculate_security_score

model = joblib.load(
    "models/repository_health_model.pkl"
)

repo_name = input(
    "Enter repository (owner/repo): "
)

repo_data = get_repository_info(repo_name)

documentation_score = calculate_documentation_score(repo_data)
activity_score = calculate_activity_score(repo_data)
community_score = calculate_community_score(repo_data)
security_score = calculate_security_score(repo_data)
health_score = calculate_health_score(
    documentation_score,
    activity_score,
    community_score,
    security_score
)
features = pd.DataFrame([
    {
        "stars": repo_data["stars"],
        "forks": repo_data["forks"],
        "watchers": repo_data["watchers"],
        "contributors": repo_data["contributors"],
        "commits": repo_data["commits"],
        "releases": repo_data["releases"],
        "open_issues": repo_data["open_issues"],
        "documentation_score": documentation_score,
        "activity_score": activity_score,
        "community_score": community_score,
        "security_score": security_score
    }
])
prediction = model.predict(features)

prediction = model.predict(features)

print("\nRepository:", repo_name)

print("\nDocumentation Score:", documentation_score)
print("Activity Score:", activity_score)
print("Community Score:", community_score)
print("Security Score:", security_score)

print("\nHealth Score:", health_score)

print("\nPrediction:", prediction[0])