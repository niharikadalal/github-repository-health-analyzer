import pandas as pd

df = pd.read_csv("data/raw/repositories.csv")

print(df["label"].value_counts())