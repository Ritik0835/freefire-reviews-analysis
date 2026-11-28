from pathlib import Path

import pandas as pd

SOURCE = Path("data/categorized_reviews.csv")
OLD = Path("data/validation_sample.csv")
OUT = Path("data/fresh_sample.csv")
PER_LANGUAGE = 30

df = pd.read_csv(SOURCE)
old_ids = set(pd.read_csv(OLD)["review_id"])

pool = df[
    (df["rating_group"] == "negative")
    & (df["content_length"] >= 10)
    & (~df["review_id"].isin(old_ids))
]
sample = pool.groupby("language").sample(PER_LANGUAGE, random_state=2026)
sample = sample.sample(frac=1, random_state=11)  # shuffle languages together
sample[["review_id", "language", "content"]].to_csv(OUT, index=False)

print("Wrote", len(sample), "reviews to", OUT)
print(sample["language"].value_counts().to_dict())
print("Overlap with the old sample:", len(set(sample["review_id"]) & old_ids))
