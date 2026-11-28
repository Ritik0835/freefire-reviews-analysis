from pathlib import Path

import pandas as pd

from categorize_reviews import GENERAL_NAME, SPECIFIC, categorize

SAMPLE = Path("data/fresh_sample.csv")
LABELS = Path("validation/fresh_labels.csv")
OUT = Path("validation/scores_fresh_v3.csv")
CATS = SPECIFIC + [GENERAL_NAME]

sample = pd.read_csv(SAMPLE)
labels = pd.read_csv(LABELS)
df = labels.merge(sample[["review_id", "content"]], on="review_id")
assert len(df) == 120

flags = pd.DataFrame([categorize(t) for t in df["content"]], index=df.index)
truth = {c: df["true_labels"].str.split("|").apply(lambda xs, c=c: c in xs) for c in CATS}


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else float("nan")
    r = tp / (tp + fn) if tp + fn else float("nan")
    f = 2 * p * r / (p + r) if (p == p and r == r and p + r > 0) else float("nan")
    return p, r, f


rows = []
for c in CATS:
    t, g = truth[c], flags[c].astype(bool)
    tp = int((t & g).sum())
    fp = int((~t & g).sum())
    fn = int((t & ~g).sum())
    p, r, f = prf(tp, fp, fn)
    rows.append({"category": c, "true_count": int(t.sum()), "predicted_count": int(g.sum()),
                 "tp": tp, "fp": fp, "fn": fn, "precision": round(p, 2),
                 "recall": round(r, 2), "f1": round(f, 2)})

tot = {k: sum(r[k] for r in rows) for k in ["tp", "fp", "fn"]}
p, r, f = prf(tot["tp"], tot["fp"], tot["fn"])
rows.append({"category": "ALL (pooled)", "true_count": sum(x["true_count"] for x in rows),
             "predicted_count": sum(x["predicted_count"] for x in rows),
             "tp": tot["tp"], "fp": tot["fp"], "fn": tot["fn"],
             "precision": round(p, 2), "recall": round(r, 2), "f1": round(f, 2)})

scores = pd.DataFrame(rows)
print("\nTuned categorizer on the fresh held-out sample (120 reviews)")
print(scores.to_string(index=False))

print("\nBy language market (all categories pooled)")
for lang, g_df in df.groupby("language"):
    idx = g_df.index
    tp = sum(int((truth[c][idx] & flags[c][idx]).sum()) for c in CATS)
    fp = sum(int((~truth[c][idx] & flags[c][idx]).sum()) for c in CATS)
    fn = sum(int((truth[c][idx] & ~flags[c][idx]).sum()) for c in CATS)
    p, r, f = prf(tp, fp, fn)
    print(f"  {lang}: precision {p:.2f}, recall {r:.2f}, f1 {f:.2f}")

none_rows = df["true_labels"] == "none"
flagged = int(flags.loc[none_rows, SPECIFIC].any(axis=1).sum())
print(f"\nReviews labelled 'none': {int(none_rows.sum())}; "
      f"the categorizer gave {flagged} of them a specific category")

scores.to_csv(OUT, index=False)
print(f"\nSaved {OUT}")
