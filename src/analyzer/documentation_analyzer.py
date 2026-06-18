def calculate_documentation_score(repo_data):

    score = 0

    if repo_data["readme_present"]:
        score += 40

    if repo_data["license"] != "No License":
        score += 30

    if repo_data["contributing_present"]:
        score += 15

    if repo_data["security_present"]:
        score += 15

    return score