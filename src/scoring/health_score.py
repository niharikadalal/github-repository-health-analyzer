def calculate_health_score(
    documentation_score,
    activity_score,
    community_score,
    security_score
):

    health_score = (
        documentation_score * 0.25 +
        activity_score * 0.30 +
        community_score * 0.25 +
        security_score * 0.20
    )

    return round(health_score, 2)