
from src.analyzer.activity_analyzer import calculate_activity_score
from src.collector.github_collector import get_repository_info
from src.analyzer.documentation_analyzer import calculate_documentation_score
from src.analyzer.activity_analyzer import calculate_activity_score
from src.analyzer.community_analyzer import calculate_community_score
from src.analyzer.security_analyzer import calculate_security_score
from src.scoring.health_score import calculate_health_score
repo_data = get_repository_info("996icu/996.ICU")

for key, value in repo_data.items():
    print(f"{key}: {value}")

print()
print(
    "Documentation Score:",
    calculate_documentation_score(repo_data)
)
print(
    "Activity Score:",
    calculate_activity_score(repo_data)
)
print(
    "Community Score:",
    calculate_community_score(repo_data)
)
print(
    "Security Score:",
    calculate_security_score(repo_data)
)
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

print("\nHealth Score:", health_score)