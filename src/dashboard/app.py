import sys
from pathlib import Path
from urllib.parse import urlparse

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


# ============================================================
# PROJECT IMPORTS
# ============================================================

from src.collector.github_collector import get_repository_info

from src.analyzer.documentation_analyzer import (
    calculate_documentation_score
)

from src.analyzer.activity_analyzer import (
    calculate_activity_score
)

from src.analyzer.community_analyzer import (
    calculate_community_score
)

from src.analyzer.security_analyzer import (
    calculate_security_score
)

from src.analyzer.maturity_analyzer import (
    calculate_maturity_score,
    classify_repository_maturity
)

from src.scoring.health_score import (
    calculate_health_score
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="GitHub Repository Health Analyzer",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1250px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }

    #MainMenu,
    footer,
    header {
        visibility: hidden;
    }

    .app-subtitle {
        color: #9ca3af;
        font-size: 1rem;
        margin-top: -0.5rem;
        margin-bottom: 1.5rem;
    }

    .repo-box {
        padding: 1rem 1.2rem;
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 14px;
        background: rgba(128,128,128,.07);
        margin: .8rem 0 1.2rem 0;
    }

    .score-number {
        font-size: 1.9rem;
        font-weight: 750;
    }

    .small-muted {
        color: #9ca3af;
        font-size: .85rem;
    }

    .action-box {
        padding: 1rem 1.1rem;
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 12px;
        margin-bottom: .7rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.22);
        border-radius: 12px;
        padding: 12px 14px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.55rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPERS
# ============================================================

def normalize_repo_input(value):
    """
    Convert:

        https://github.com/pallets/flask
        github.com/pallets/flask
        pallets/flask

    into:

        pallets/flask
    """

    value = value.strip()

    if not value:
        return ""

    if "github.com" in value:

        parsed = urlparse(
            value
            if "://" in value
            else "https://" + value
        )

        parts = [
            part
            for part in parsed.path.strip("/").split("/")
            if part
        ]

        if len(parts) >= 2:

            return (
                f"{parts[-2]}/"
                f"{parts[-1].replace('.git', '')}"
            )

    return value.strip("/")


def number(value):

    try:
        return f"{int(value):,}"

    except (TypeError, ValueError):

        return "N/A"


def commit_age(days):

    if days is None:
        return "Unknown"

    try:
        days = int(days)

    except (TypeError, ValueError):

        return "Unknown"

    if days == 0:
        return "Today"

    if days == 1:
        return "1 day ago"

    return f"{days:,} days ago"


def score_status(score):

    try:
        score = float(score)

    except (TypeError, ValueError):

        return "Unknown"

    if score >= 80:
        return "Strong"

    if score >= 60:
        return "Needs attention"

    return "Weak"


def score_help(name, score):

    try:
        score = float(score)

    except (TypeError, ValueError):

        return ""

    descriptions = {

        "Documentation":
            (
                "Clear project and contribution documentation."
                if score >= 80
                else
                "README and supporting documentation can be improved."
            ),

        "Activity":
            (
                "Repository shows healthy maintenance activity."
                if score >= 80
                else
                "Recent development activity could be stronger."
            ),

        "Community":
            (
                "Contributor and community engagement is healthy."
                if score >= 80
                else
                "Community participation could be improved."
            ),

        "Security":
            (
                "Visible security practices are in good shape."
                if score >= 80
                else
                "More security controls and automation are recommended."
            )
    }

    return descriptions.get(name, "")


def show_score_card(column, name, score):

    try:
        value = float(score)

    except (TypeError, ValueError):

        value = 0

    with column:

        st.markdown(f"**{name}**")

        st.markdown(
            f"""
            <div class="score-number">
                {value:.0f}
                <span class="small-muted">
                    / 100
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.progress(
            max(
                0.0,
                min(
                    value / 100,
                    1.0
                )
            )
        )

        st.caption(
            f"{score_status(value)} · "
            f"{score_help(name, value)}"
        )


def model_feature_frame(model, values):

    if hasattr(
        model,
        "feature_names_in_"
    ):

        names = list(
            model.feature_names_in_
        )

    else:

        names = list(
            values.keys()
        )

    return pd.DataFrame(
        [
            {
                name:
                    values.get(
                        name,
                        0
                    )
                for name in names
            }
        ]
    )


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model():

    return joblib.load(
        PROJECT_ROOT
        / "models"
        / "repository_health_model.pkl"
    )


# ============================================================
# ANALYZE REPOSITORY
# ============================================================

def analyze_repository(repo_name):

    repo = get_repository_info(
        repo_name
    )


    # --------------------------------------------------------
    # HEALTH DIMENSIONS
    # --------------------------------------------------------

    documentation = calculate_documentation_score(
        repo
    )

    activity = calculate_activity_score(
        repo
    )

    community = calculate_community_score(
        repo
    )

    security = calculate_security_score(
        repo
    )


    # --------------------------------------------------------
    # OVERALL HEALTH
    # --------------------------------------------------------

    health = calculate_health_score(
        documentation,
        activity,
        community,
        security
    )


    # --------------------------------------------------------
    # MATURITY
    # --------------------------------------------------------

    maturity_score = calculate_maturity_score(
        repo
    )

    maturity_stage = classify_repository_maturity(
        maturity_score
    )


    # --------------------------------------------------------
    # MODEL FEATURES
    # --------------------------------------------------------

    feature_values = {

        "stars":
            repo.get(
                "stars",
                0
            ),

        "forks":
            repo.get(
                "forks",
                0
            ),

        "watchers":
            repo.get(
                "watchers",
                0
            ),

        "contributors":
            repo.get(
                "contributors",
                0
            ),

        "commits":
            repo.get(
                "commits",
                0
            ),

        "releases":
            repo.get(
                "releases",
                0
            ),

        "open_issues":
            repo.get(
                "open_issues",
                0
            ),

        "open_prs":
            repo.get(
                "open_prs",
                0
            ),

        "closed_prs":
            repo.get(
                "closed_prs",
                0
            ),

        "repo_age_days":
            repo.get(
                "repo_age_days",
                0
            ),

        "last_commit_days":
            repo.get(
                "last_commit_days",
                0
            ),

        "documentation_score":
            documentation,

        "activity_score":
            activity,

        "community_score":
            community,

        "security_score":
            security,

        "readme_present":
            repo.get(
                "readme_present",
                False
            ),

        "contributing_present":
            repo.get(
                "contributing_present",
                False
            ),

        "docs_present":
            repo.get(
                "docs_present",
                False
            ),

        "examples_present":
            repo.get(
                "examples_present",
                False
            ),

        "security_present":
            repo.get(
                "security_present",
                False
            ),

        "dependabot_present":
            repo.get(
                "dependabot_present",
                False
            ),

        "codeql_present":
            repo.get(
                "codeql_present",
                False
            ),

        "code_of_conduct_present":
            repo.get(
                "code_of_conduct_present",
                False
            )
    }


    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    model = load_model()

    features = model_feature_frame(
        model,
        feature_values
    )


    prediction = model.predict(
        features
    )[0]


    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    confidence = None

    if hasattr(
        model,
        "predict_proba"
    ):

        probabilities = model.predict_proba(
            features
        )[0]

        confidence = float(
            max(probabilities) * 100
        )


    # --------------------------------------------------------
    # FEATURE IMPORTANCE
    # --------------------------------------------------------

    importance = None

    if hasattr(
        model,
        "feature_importances_"
    ):

        if hasattr(
            model,
            "feature_names_in_"
        ):

            feature_names = list(
                model.feature_names_in_
            )

        else:

            feature_names = list(
                features.columns
            )

        importance = pd.DataFrame(
            {
                "Feature":
                    feature_names,

                "Importance":
                    model.feature_importances_
            }
        ).sort_values(
            "Importance",
            ascending=False
        )


    return {

        "repo":
            repo,

        "documentation":
            documentation,

        "activity":
            activity,

        "community":
            community,

        "security":
            security,

        "health":
            health,

        "maturity_score":
            maturity_score,

        "maturity_stage":
            maturity_stage,

        "prediction":
            prediction,

        "confidence":
            confidence,

        "importance":
            importance
    }


# ============================================================
# HEADER
# ============================================================

st.title(
    "GitHub Repository Health Analyzer"
)

st.markdown(
    """
    <div class="app-subtitle">
        Assess repository health, maintainability,
        community activity, security readiness
        and maturity in one place.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# INPUT
# ============================================================

repo_input = st.text_input(
    "GitHub repository",
    placeholder=(
        "https://github.com/pallets/flask "
        "or pallets/flask"
    )
)


analyze = st.button(
    "🔎 Analyze Repository",
    type="primary"
)


# ============================================================
# RUN ANALYSIS
# ============================================================

if analyze:

    repo_name = normalize_repo_input(
        repo_input
    )


    if (
        not repo_name
        or "/" not in repo_name
    ):

        st.error(
            "Enter a valid GitHub repository, "
            "for example: pallets/flask"
        )

    else:

        try:

            with st.spinner(
                "Analyzing repository..."
            ):

                st.session_state[
                    "analysis"
                ] = analyze_repository(
                    repo_name
                )

                st.session_state[
                    "repo_name"
                ] = repo_name


            st.success(
                "Repository analyzed successfully."
            )


        except Exception as exc:

            st.error(
                "Unable to analyze the repository."
            )

            st.exception(
                exc
            )


# ============================================================
# EMPTY STATE
# ============================================================

if "analysis" not in st.session_state:

    st.info(
        "Enter a repository above and click "
        "**Analyze Repository**."
    )

    st.stop()


# ============================================================
# GET RESULTS
# ============================================================

result = st.session_state[
    "analysis"
]

repo = result[
    "repo"
]

repo_name = st.session_state[
    "repo_name"
]

documentation = result[
    "documentation"
]

activity = result[
    "activity"
]

community = result[
    "community"
]

security = result[
    "security"
]

health = result[
    "health"
]

maturity_score = result[
    "maturity_score"
]

maturity_stage = result[
    "maturity_stage"
]

prediction = result[
    "prediction"
]

confidence = result[
    "confidence"
]

importance = result[
    "importance"
]


# ============================================================
# REPOSITORY HEADER
# ============================================================

st.divider()

st.subheader(
    repo_name
)

st.caption(
    repo.get(
        "description"
    )
    or
    "No repository description available."
)

st.link_button(
    "Open repository on GitHub ↗",
    f"https://github.com/{repo_name}"
)


# ============================================================
# OVERALL HEALTH
# ============================================================

st.divider()

st.subheader(
    "Overall Health"
)

health_col, prediction_col = st.columns(
    [1.4, 1]
)


with health_col:

    st.metric(
        "Repository Health",
        f"{float(health):.1f} / 100"
    )

    st.progress(
        max(
            0.0,
            min(
                float(health) / 100,
                1.0
            )
        )
    )


with prediction_col:

    st.metric(
        "ML Assessment",
        str(prediction)
    )

    if confidence is not None:

        st.caption(
            f"Model confidence: "
            f"{confidence:.1f}%"
        )

    else:

        st.caption(
            "Model confidence unavailable."
        )


# ============================================================
# CORE HEALTH DIMENSIONS
# ============================================================

st.subheader(
    "Health Dimensions"
)

st.caption(
    "Four independent dimensions used to assess repository health."
)


score_columns = st.columns(4)


for col, name, value in zip(

    score_columns,

    [
        "Documentation",
        "Activity",
        "Community",
        "Security"
    ],

    [
        documentation,
        activity,
        community,
        security
    ]
):

    show_score_card(
        col,
        name,
        value
    )


# ============================================================
# REPOSITORY SNAPSHOT
# ============================================================

st.subheader(
    "Repository Snapshot"
)

snapshot = st.columns(5)


with snapshot[0]:

    st.metric(
        "⭐ Stars",
        number(
            repo.get(
                "stars"
            )
        )
    )


with snapshot[1]:

    st.metric(
        "🍴 Forks",
        number(
            repo.get(
                "forks"
            )
        )
    )


with snapshot[2]:

    st.metric(
        "👥 Contributors",
        number(
            repo.get(
                "contributors"
            )
        )
    )


with snapshot[3]:

    st.metric(
        "📦 Releases",
        number(
            repo.get(
                "releases"
            )
        )
    )


with snapshot[4]:

    st.metric(
        "⏱ Last Commit",
        commit_age(
            repo.get(
                "last_commit_days"
            )
        )
    )


# ============================================================
# TABS
# ============================================================

(
    summary_tab,
    maturity_tab,
    risks_tab,
    ml_tab,
    details_tab
) = st.tabs(
    [
        "Summary",
        "Maturity",
        "Risks & Actions",
        "ML Insights",
        "Repository Details"
    ]
)


# ============================================================
# SUMMARY
# ============================================================

with summary_tab:

    st.subheader(
        "What stands out"
    )


    scores = {

        "Documentation":
            float(
                documentation
            ),

        "Activity":
            float(
                activity
            ),

        "Community":
            float(
                community
            ),

        "Security":
            float(
                security
            )
    }


    strongest = max(
        scores,
        key=scores.get
    )

    weakest = min(
        scores,
        key=scores.get
    )


    c1, c2 = st.columns(2)


    with c1:

        st.success(
            f"**Strongest area:** "
            f"{strongest} — "
            f"{scores[strongest]:.0f}/100"
        )


    with c2:

        if scores[weakest] < 60:

            st.error(
                f"**Priority area:** "
                f"{weakest} — "
                f"{scores[weakest]:.0f}/100"
            )

        else:

            st.warning(
                f"**Priority area:** "
                f"{weakest} — "
                f"{scores[weakest]:.0f}/100"
            )


    st.subheader(
        "Quick assessment"
    )


    assessment = []


    if security < 60:

        assessment.append(
            (
                "Security",
                "Security controls need attention."
            )
        )

    elif security >= 80:

        assessment.append(
            (
                "Security",
                "Visible security practices are strong."
            )
        )


    if documentation < 60:

        assessment.append(
            (
                "Documentation",
                "Documentation coverage is limited."
            )
        )

    elif documentation >= 80:

        assessment.append(
            (
                "Documentation",
                "Documentation coverage is strong."
            )
        )


    if activity < 60:

        assessment.append(
            (
                "Activity",
                "Recent repository activity is low."
            )
        )

    elif activity >= 80:

        assessment.append(
            (
                "Activity",
                "Repository activity is healthy."
            )
        )


    if community < 60:

        assessment.append(
            (
                "Community",
                "Community engagement is limited."
            )
        )

    elif community >= 80:

        assessment.append(
            (
                "Community",
                "Community engagement is healthy."
            )
        )


    if assessment:

        for title, message in assessment:

            st.write(
                f"**{title}:** {message}"
            )

    else:

        st.info(
            "No major strengths or weaknesses stand out."
        )


# ============================================================
# MATURITY
# ============================================================

with maturity_tab:

    st.subheader(
        "Repository Maturity"
    )


    st.metric(
        "Maturity Score",
        f"{float(maturity_score):.0f} / 100",
        delta=str(
            maturity_stage
        )
    )


    age_days = repo.get(
        "repo_age_days"
    )


    try:

        age_years = (
            float(age_days)
            / 365.25
        )

        age_text = (
            f"{age_years:.1f} years"
        )

    except (
        TypeError,
        ValueError
    ):

        age_text = "Unknown"


    maturity_cols = st.columns(4)


    with maturity_cols[0]:

        st.metric(
            "Repository Age",
            age_text
        )


    with maturity_cols[1]:

        st.metric(
            "Contributors",
            number(
                repo.get(
                    "contributors"
                )
            )
        )


    with maturity_cols[2]:

        st.metric(
            "Commits",
            number(
                repo.get(
                    "commits"
                )
            )
        )


    with maturity_cols[3]:

        st.metric(
            "Releases",
            number(
                repo.get(
                    "releases"
                )
            )
        )


    st.caption(
        "Maturity is calculated separately from "
        "the four core health dimensions."
    )


# ============================================================
# RISKS & ACTIONS
# ============================================================

with risks_tab:

    st.subheader(
        "Risks"
    )


    risks = []


    if documentation < 75:

        risks.append(
            (
                "📚 Documentation",
                "Documentation coverage is below the preferred level.",
                "Improve the README and supporting project documentation."
            )
        )


    if security < 60:

        risks.append(
            (
                "🔐 Security",
                "Visible security controls are limited.",
                "Add security policies and automated security checks."
            )
        )


    last_commit_days = repo.get(
        "last_commit_days"
    )


    if (
        isinstance(
            last_commit_days,
            (int, float)
        )
        and last_commit_days > 180
    ):

        risks.append(
            (
                "⏳ Activity",
                "The last recorded commit is more than six months old.",
                "Review maintenance activity and release cadence."
            )
        )


    if repo.get(
        "open_issues",
        0
    ) > 1000:

        risks.append(
            (
                "🐛 Issue backlog",
                "The repository has a very large number of open issues.",
                "Review, prioritize and close obsolete issues."
            )
        )


    if not repo.get(
        "security_present",
        False
    ):

        risks.append(
            (
                "🛡 SECURITY.md",
                "A dedicated security policy was not detected.",
                "Add SECURITY.md with vulnerability reporting guidance."
            )
        )


    if not repo.get(
        "dependabot_present",
        False
    ):

        risks.append(
            (
                "📦 Dependencies",
                "Dependabot was not detected.",
                "Enable Dependabot for automated dependency monitoring."
            )
        )


    if not risks:

        st.success(
            "No major risks detected from the current analysis."
        )

    else:

        for title, message, action in risks:

            st.markdown(
                f"""
<div class="action-box">
    <strong>{title}</strong>
    <br><br>
    {message}
    <br><br>
    <span class="small-muted">
        Recommended: {action}
    </span>
</div>
                """,
                unsafe_allow_html=True
            )


    st.subheader(
        "Recommended Actions"
    )


    recommendations = []


    if documentation < 80:

        recommendations.append(
            "Improve README and project documentation."
        )


    if not repo.get(
        "security_present",
        False
    ):

        recommendations.append(
            "Add SECURITY.md and security reporting guidance."
        )


    if not repo.get(
        "dependabot_present",
        False
    ):

        recommendations.append(
            "Enable Dependabot for dependency monitoring."
        )


    if not repo.get(
        "codeql_present",
        False
    ):

        recommendations.append(
            "Consider enabling GitHub CodeQL scanning."
        )


    if not repo.get(
        "contributing_present",
        False
    ):

        recommendations.append(
            "Add CONTRIBUTING.md for contributors."
        )


    if community < 80:

        recommendations.append(
            "Improve contributor and community engagement."
        )


    if activity < 80:

        recommendations.append(
            "Review maintenance and release frequency."
        )


    if recommendations:

        for i, item in enumerate(
            recommendations,
            1
        ):

            st.write(
                f"**{i}.** {item}"
            )

    else:

        st.success(
            "No major actions are recommended."
        )


# ============================================================
# ML INSIGHTS
# ONE CHART ONLY
# ============================================================

with ml_tab:

    st.subheader(
        "Machine Learning Insights"
    )


    ml1, ml2 = st.columns(2)


    with ml1:

        st.metric(
            "Prediction",
            str(
                prediction
            )
        )


    with ml2:

        st.metric(
            "Confidence",
            (
                f"{confidence:.1f}%"
                if confidence is not None
                else "N/A"
            )
        )


    if (
        importance is not None
        and not importance.empty
    ):

        st.subheader(
            "Most Important Model Features"
        )


        readable = {

            "stars":
                "Stars",

            "forks":
                "Forks",

            "watchers":
                "Watchers",

            "contributors":
                "Contributors",

            "commits":
                "Commits",

            "releases":
                "Releases",

            "open_issues":
                "Open Issues",

            "open_prs":
                "Open PRs",

            "closed_prs":
                "Closed PRs",

            "repo_age_days":
                "Repository Age",

            "last_commit_days":
                "Last Commit Age",

            "documentation_score":
                "Documentation Score",

            "activity_score":
                "Activity Score",

            "community_score":
                "Community Score",

            "security_score":
                "Security Score",

            "readme_present":
                "README",

            "contributing_present":
                "CONTRIBUTING.md",

            "docs_present":
                "Documentation",

            "examples_present":
                "Examples",

            "security_present":
                "SECURITY.md",

            "dependabot_present":
                "Dependabot",

            "codeql_present":
                "CodeQL",

            "code_of_conduct_present":
                "Code of Conduct"
        }


        chart_data = (
            importance
            .head(8)
            .copy()
        )


        chart_data["Feature"] = (
            chart_data[
                "Feature"
            ].map(
                lambda x:
                    readable.get(
                        x,
                        x
                    )
            )
        )


        chart_data = (
            chart_data
            .sort_values(
                "Importance"
            )
        )


        fig = px.bar(
            chart_data,
            x="Importance",
            y="Feature",
            orientation="h",
            title="Top 8 Features"
        )


        fig.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=20,
                t=55,
                b=20
            ),
            xaxis_title="Model importance",
            yaxis_title="",
            showlegend=False
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


        st.caption(
            "This shows which input features "
            "had the greatest importance to the "
            "trained Random Forest model."
        )


    else:

        st.info(
            "Feature importance is not available "
            "for this model."
        )


# ============================================================
# REPOSITORY DETAILS
# ============================================================

with details_tab:

    st.subheader(
        "Repository Details"
    )


    basic = {

        "Repository":
            repo_name,

        "Description":
            repo.get(
                "description"
            )
            or "N/A",

        "License":
            repo.get(
                "license"
            )
            or "N/A",

        "Created":
            repo.get(
                "created_at"
            )
            or "N/A",

        "Last Updated":
            repo.get(
                "updated_at"
            )
            or "N/A"
    }


    development = {

        "Open Issues":
            number(
                repo.get(
                    "open_issues"
                )
            ),

        "Open Pull Requests":
            number(
                repo.get(
                    "open_prs"
                )
            ),

        "Closed Pull Requests":
            number(
                repo.get(
                    "closed_prs"
                )
            ),

        "Watchers":
            number(
                repo.get(
                    "watchers"
                )
            ),

        "Forks":
            number(
                repo.get(
                    "forks"
                )
            )
    }


    c1, c2 = st.columns(2)


    with c1:

        st.markdown(
            "**Basic Information**"
        )


        st.dataframe(
            pd.DataFrame(
                list(
                    basic.items()
                ),
                columns=[
                    "Field",
                    "Value"
                ]
            ),
            use_container_width=True,
            hide_index=True
        )


    with c2:

        st.markdown(
            "**Development Information**"
        )


        st.dataframe(
            pd.DataFrame(
                list(
                    development.items()
                ),
                columns=[
                    "Field",
                    "Value"
                ]
            ),
            use_container_width=True,
            hide_index=True
        )


    st.subheader(
        "Repository Resources"
    )


    resources = {

        "README":
            repo.get(
                "readme_present",
                False
            ),

        "CONTRIBUTING.md":
            repo.get(
                "contributing_present",
                False
            ),

        "SECURITY.md":
            repo.get(
                "security_present",
                False
            ),

        "CODE_OF_CONDUCT.md":
            repo.get(
                "code_of_conduct_present",
                False
            ),

        "Documentation":
            repo.get(
                "docs_present",
                False
            ),

        "Examples":
            repo.get(
                "examples_present",
                False
            ),

        "Dependabot":
            repo.get(
                "dependabot_present",
                False
            ),

        "CodeQL":
            repo.get(
                "codeql_present",
                False
            )
    }


    resource_df = pd.DataFrame(
        [
            {
                "Resource":
                    name,

                "Status":
                    (
                        "✓ Present"
                        if present
                        else
                        "✗ Not detected"
                    )
            }

            for name, present
            in resources.items()
        ]
    )


    st.dataframe(
        resource_df,
        use_container_width=True,
        hide_index=True
    )
