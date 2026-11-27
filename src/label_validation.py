import csv
import textwrap
from pathlib import Path

import pandas as pd

SOURCE = Path("data/categorized_reviews.csv")
SAMPLE = Path("data/validation_sample.csv")
LABELS = Path("validation/validation_labels.csv")
PER_LANGUAGE = 60

OPTIONS = {
    "1": "lag_performance",
    "2": "server_connection",
    "3": "download_open_crash",
    "4": "hackers_cheaters",
    "5": "pricing_pay2win",
    "6": "payment_missing_items",
    "7": "matchmaking_balance",
    "8": "bugs_glitches",
    "9": "account_ban_loss",
    "10": "content_events_changes",
    "11": "device_optimization",
    "12": "general_negative",
    "0": "none",
}

LABELS.parent.mkdir(exist_ok=True)

# Fixed random sample, created once and reused in every session
if not SAMPLE.exists():
    df = pd.read_csv(SOURCE)
    pool = df[(df["rating_group"] == "negative") & (df["content_length"] >= 10)]
    sample = pool.groupby("language").sample(PER_LANGUAGE, random_state=42)
    sample = sample.sample(frac=1, random_state=7)  # shuffle languages together
    sample[["review_id", "language", "content"]].to_csv(SAMPLE, index=False)

sample = pd.read_csv(SAMPLE)
if LABELS.exists():
    done_ids = set(pd.read_csv(LABELS)["review_id"])
else:
    done_ids = set()
todo = sample[~sample["review_id"].isin(done_ids)]
n_done = len(done_ids)

print("\nLabel what each review COMPLAINS ABOUT. You can give several, e.g. 1,8")
for code, name in OPTIONS.items():
    print(f"  {code:>2} = {name}")
print("Use 12 for a general complaint with no specific cause (e.g. 'worst game').")
print("Use 0 if it is not a complaint about the game (praise, off-topic, unclear).")
print(f"\n{n_done} of {len(sample)} done, {len(todo)} left.\n")


def save(review_id, language, names):
    new_file = not LABELS.exists()
    with open(LABELS, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["review_id", "language", "true_labels"])
        writer.writerow([review_id, language, "|".join(names)])


for row in todo.itertuples():
    print("\n" + "=" * 70)
    print(f"[{n_done + 1}/{len(sample)}]  market: {row.language}")
    print(textwrap.fill(str(row.content), 70))
    while True:
        answer = input("labels (e.g. 1,8) | s=skip | q=quit > ").strip().lower()
        if answer == "q":
            print(f"\nSaved. {n_done} of {len(sample)} done.")
            raise SystemExit
        if answer == "s":
            break
        codes = [c.strip() for c in answer.split(",") if c.strip()]
        valid = codes and all(c in OPTIONS for c in codes)
        if valid and "0" in codes and len(codes) > 1:
            valid = False
        if not valid:
            print("  Please enter codes from the list, e.g. 1,8 or 0")
            continue
        save(row.review_id, row.language, sorted({OPTIONS[c] for c in codes}))
        n_done += 1
        break

print(f"\nAll done: {n_done} of {len(sample)} labelled.")
