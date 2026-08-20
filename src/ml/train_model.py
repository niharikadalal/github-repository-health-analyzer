import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# Load Dataset
df = pd.read_csv("data/raw/repositories.csv")

# Features
X = df[
    [
        "stars",
        "forks",
        "watchers",
        "contributors",
        "commits",
        "releases",
        "open_issues",
        "open_prs",
        "closed_prs",
        "repo_age_days",
        "last_commit_days",
        "documentation_score",
        "activity_score",
        "community_score",
        "security_score",
        "readme_present",
        "contributing_present",
        "docs_present",
        "examples_present",
        "security_present",
        "dependabot_present",
        "codeql_present",
        "code_of_conduct_present"
    ]
]

# Target
y = df["label"]

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)

# Train
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Results
print("\nAccuracy:")
print(accuracy_score(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
import joblib

joblib.dump(model, "models/repository_health_model.pkl")

print("Model saved successfully!")
feature_importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
})

print("\nFeature Importance:")
print(
    feature_importance.sort_values(
        by="Importance",
        ascending=False
    )
)