import pandas as pd

sample = pd.read_csv("data/validation_sample.csv")
labels = pd.read_csv("validation/validation_labels.csv")
df = sample.merge(labels[["review_id", "true_labels"]], on="review_id")

for i, r in df.sample(30, random_state=1).iterrows():
    print("-" * 70)
    print(f"#{i} [{r.language}] {' '.join(str(r.content).split())[:300]}")
    print(f"   LABEL: {r.true_labels}")
