def calculate_community_score(repo_data):

    score = 0

    # Contributors
    if repo_data["contributors"] > 100:
        score += 50
    elif repo_data["contributors"] > 20:
        score += 40
    elif repo_data["contributors"] > 5:
        score += 30
    else:
        score += 10

    # Issues
    if repo_data["open_issues"] < 10:
        score += 50
    elif repo_data["open_issues"] < 50:
        score += 40
    elif repo_data["open_issues"] < 100:
        score += 30
    else:
        score += 10

    return score