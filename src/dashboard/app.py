import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]

if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
import streamlit as st
import pandas as pd
import joblib

from src.collector.github_collector import get_repository_info

from src.analyzer.documentation_analyzer import calculate_documentation_score
from src.analyzer.activity_analyzer import calculate_activity_score
from src.analyzer.community_analyzer import calculate_community_score
from src.analyzer.security_analyzer import calculate_security_score

from src.scoring.health_score import calculate_health_score

def normalize_repo_input(repo_input):

    repo_input = repo_input.strip()

    if "github.com" in repo_input:

        repo_input = repo_input.rstrip("/")

        parts = repo_input.split("/")

        return f"{parts[-2]}/{parts[-1]}"

    return repo_input

st.set_page_config(
    page_title="GitHub Repository Health Analyzer",
    layout="wide"
)

st.title("GitHub Repository Health Analyzer")

repo_input = st.text_input(
    "Repository URL or owner/repository",
    placeholder="https://github.com/pallets/flask"
)

if st.button("Analyze Repository"):

    try:

        model = joblib.load(
            "models/repository_health_model.pkl"
        )
        repo_name = normalize_repo_input(repo_input)
        repo_data = get_repository_info(repo_name)

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

        prediction = model.predict(features)[0]

        overview_tab, metrics_tab, details_tab, recommendations_tab = st.tabs(
            [
                "Overview",
                "Metrics",
                "Repository Details",
                "Recommendations"
            ]
        )

        with overview_tab:

            c1, c2, c3 = st.columns(3)

            c1.metric("⭐ Stars", repo_data["stars"])
            c2.metric("🍴 Forks", repo_data["forks"])
            c3.metric("👥 Contributors", repo_data["contributors"])

            st.metric("💖 Health Score", health_score)

            if prediction == "Healthy":
                st.success(f"Prediction: {prediction}")

            elif prediction == "Moderately Healthy":
                st.warning(f"Prediction: {prediction}")

            else:
                st.error(f"Prediction: {prediction}")

        with metrics_tab:

            st.write("Documentation")
            st.progress(documentation_score / 100)

            st.write("Activity")
            st.progress(activity_score / 100)

            st.write("Community")
            st.progress(community_score / 100)

            st.write("Security")
            st.progress(security_score / 100)

        with details_tab:

            st.write("Repository:", repo_name)
            st.write("Description:", repo_data["description"])
            st.write("License:", repo_data["license"])
            st.write("Watchers:", repo_data["watchers"])
            st.write("Commits:", repo_data["commits"])
            st.write("Releases:", repo_data["releases"])
            st.write("Created:", repo_data["created_at"])
            st.write("Updated:", repo_data["updated_at"])

        with recommendations_tab:

            recommendations = []

            if documentation_score < 80:
                recommendations.append(
                    "Improve README and documentation."
                )

            if security_score < 80:
                recommendations.append(
                    "Add SECURITY.md and security guidelines."
                )

            if community_score < 80:
                recommendations.append(
                    "Add contribution guidelines."
                )

            if activity_score < 80:
                recommendations.append(
                    "Increase maintenance and release frequency."
                )

            if recommendations:

                for rec in recommendations:
                    st.write("✓", rec)

            else:
                st.success(
                    "No major improvements suggested."
                )

    except Exception as e:

        st.error(str(e))