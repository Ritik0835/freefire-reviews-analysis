import pandas as pd

df = pd.read_csv("data/categorized_reviews.csv")
neg = df[df["rating_group"] == "negative"].copy()
neg["content"] = neg["content"].fillna("").astype(str).str.replace(r"\s+", " ", regex=True)

print("\n=== UNCATEGORIZED negative reviews (25+ chars) ===")
unc = neg[(neg["category_status"] == "uncategorized") & (neg["content_length"] >= 25)]
for lang, grp in unc.groupby("language"):
    print(f"\n-- {lang} ({len(grp)} reviews) --")
    for text in grp.sample(min(12, len(grp)), random_state=1)["content"]:
        print("  *", text[:140])

print("\n=== content_events_changes matches (precision check) ===")
ev = neg[neg["content_events_changes"]]
for text in ev.sample(min(20, len(ev)), random_state=1)["content"]:
    print("  *", text[:140])
