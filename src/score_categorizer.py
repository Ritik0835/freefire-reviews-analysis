from pathlib import Path

import pandas as pd

PRED = Path("data/categorized_reviews.csv")
LABELS = Path("validation/validation_labels.csv")
SCORES_OUT = Path("validation/scores_v2.csv")
ERRORS_OUT = Path("data/score_errors.csv")

CATS = [
    "lag_performance", "server_connection", "download_open_crash",
    "hackers_cheaters", "pricing_pay2win", "payment_missing_items",
    "matchmaking_balance", "bugs_glitches", "account_ban_loss",
    "content_events_changes", "device_optimization", "general_negative",
]

pred = pd.read_csv(PRED)
labels = pd.read_csv(LABELS)
df = labels.merge(pred[["review_id", "content"] + CATS], on="review_id", how="left")
assert len(df) == 240 and df[CATS].notna().all().all(), "some reviews not found"

truth = {c: df["true_labels"].str.split("|").apply(lambda xs, c=c: c in xs) for c in CATS}
guess = {c: df[c].astype(bool) for c in CATS}


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else float("nan")
    r = tp / (tp + fn) if tp + fn else float("nan")
    f = 2 * p * r / (p + r) if (p == p and r == r and p + r > 0) else float("nan")
    return p, r, f


rows, errors = [], []
for c in CATS:
    t, g = truth[c], guess[c]
    tp = int((t & g).sum())
    fp = int((~t & g).sum())
    fn = int((t & ~g).sum())
    p, r, f = prf(tp, fp, fn)
    rows.append({"category": c, "true_count": int(t.sum()),
                 "predicted_count": int(g.sum()), "tp": tp, "fp": fp, "fn": fn,
                 "precision": round(p, 2), "recall": round(r, 2), "f1": round(f, 2)})
    for idx in df.index[~t & g]:
        errors.append({"category": c, "error": "false_alarm",
                       "language": df.loc[idx, "language"],
                       "true_labels": df.loc[idx, "true_labels"],
                       "content": " ".join(str(df.loc[idx, "content"]).split())[:200]})
    for idx in df.index[t & ~g]:
        errors.append({"category": c, "error": "missed",
                       "language": df.loc[idx, "language"],
                       "true_labels": df.loc[idx, "true_labels"],
                       "content": " ".join(str(df.loc[idx, "content"]).split())[:200]})

tot = {k: sum(r[k] for r in rows) for k in ["tp", "fp", "fn"]}
p, r, f = prf(tot["tp"], tot["fp"], tot["fn"])
rows.append({"category": "ALL (pooled)", "true_count": sum(r_["true_count"] for r_ in rows),
             "predicted_count": sum(r_["predicted_count"] for r_ in rows),
             "tp": tot["tp"], "fp": tot["fp"], "fn": tot["fn"],
             "precision": round(p, 2), "recall": round(r, 2), "f1": round(f, 2)})

scores = pd.DataFrame(rows)
print("\nCategorizer vs validation labels (240 reviews)")
print(scores.to_string(index=False))

print("\nBy language market (all categories pooled)")
for lang, g_df in df.groupby("language"):
    idx = g_df.index
    tp = sum(int((truth[c][idx] & guess[c][idx]).sum()) for c in CATS)
    fp = sum(int((~truth[c][idx] & guess[c][idx]).sum()) for c in CATS)
    fn = sum(int((truth[c][idx] & ~guess[c][idx]).sum()) for c in CATS)
    p, r, f = prf(tp, fp, fn)
    print(f"  {lang}: precision {p:.2f}, recall {r:.2f}, f1 {f:.2f}")

none_rows = df["true_labels"] == "none"
flagged = int(df.loc[none_rows, CATS[:-1]].any(axis=1).sum())
print(f"\nReviews labelled 'none': {int(none_rows.sum())}; "
      f"the categorizer gave {flagged} of them a specific category")

scores.to_csv(SCORES_OUT, index=False)
pd.DataFrame(errors).to_csv(ERRORS_OUT, index=False)
print(f"\nSaved {SCORES_OUT} and {ERRORS_OUT}")
