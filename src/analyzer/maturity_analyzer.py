def calculate_maturity_score(repo_data):

    score = 0

    if repo_data["repo_age_days"] > 1825:
        score += 30
    elif repo_data["repo_age_days"] > 730:
        score += 20
    else:
        score += 10

    if repo_data["commits"] > 5000:
        score += 30
    elif repo_data["commits"] > 1000:
        score += 20
    else:
        score += 10

    if repo_data["contributors"] > 100:
        score += 20
    elif repo_data["contributors"] > 20:
        score += 15
    else:
        score += 10

    if repo_data["releases"] > 20:
        score += 20
    elif repo_data["releases"] > 5:
        score += 15
    else:
        score += 10

    return score


def classify_repository_maturity(
    maturity_score
):

    if maturity_score >= 80:
        return "Mature Project"

    elif maturity_score >= 60:
        return "Growing Project"

    else:
        return "New Project"