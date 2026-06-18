from datetime import datetime, timezone

def calculate_activity_score(repo_data):

    score = 0

    # Commit Activity
    if repo_data["commits"] > 5000:
        score += 40
    elif repo_data["commits"] > 1000:
        score += 30
    elif repo_data["commits"] > 100:
        score += 20
    else:
        score += 10

    # Release Activity
    if repo_data["releases"] > 20:
        score += 30
    elif repo_data["releases"] > 5:
        score += 20
    else:
        score += 10

    # Recent Updates
    updated_date = datetime.fromisoformat(
        repo_data["updated_at"]
    )

    days_since_update = (
        datetime.now(timezone.utc) - updated_date
    ).days

    if days_since_update <= 30:
        score += 30
    elif days_since_update <= 180:
        score += 20
    else:
        score += 10

    return score