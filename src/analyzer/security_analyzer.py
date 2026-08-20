def calculate_security_score(repo_data):

    score = 0

    # SECURITY.md
    if repo_data["security_present"]:
        score += 30

    # CodeQL security scanning
    if repo_data["codeql_present"]:
        score += 25

    # Dependabot dependency monitoring
    if repo_data["dependabot_present"]:
        score += 20

    # Code of Conduct / governance
    if repo_data["code_of_conduct_present"]:
        score += 10

    # License
    if repo_data["license"] != "No License":
        score += 15

    return score