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

st.set_page_config(
    page_title="GitHub Repository Health Analyzer",
    layout="wide"
)

st.title("GitHub Repository Health Analyzer")

repo_name = st.text_input(
    "Enter Repository (owner/repo)",
    placeholder="pallets/flask"
)

if st.button("Analyze Repository"):

    try:

        model = joblib.load(
            "models/repository_health_model.pkl"
        )

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

        st.subheader("Repository Information")

        st.write(f"**Repository:** {repo_name}")
        st.write(f"**Stars:** {repo_data['stars']}")
        st.write(f"**Forks:** {repo_data['forks']}")
        st.write(f"**Contributors:** {repo_data['contributors']}")

        st.subheader("Health Metrics")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Documentation Score",
                documentation_score
            )

            st.metric(
                "Activity Score",
                activity_score
            )

        with col2:
            st.metric(
                "Community Score",
                community_score
            )

            st.metric(
                "Security Score",
                security_score
            )

        st.metric(
            "Overall Health Score",
            health_score
        )

        st.success(
            f"Predicted Health Category: {prediction}"
        )

    except Exception as e:

        st.error(str(e))