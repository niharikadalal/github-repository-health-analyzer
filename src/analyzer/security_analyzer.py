def calculate_security_score(repo_data):

    score = 0

    if repo_data["security_present"]:
        score += 60

    if repo_data["license"] != "No License":
        score += 40

    return score