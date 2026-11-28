import csv
from pathlib import Path

import pandas as pd

SAMPLE = Path("data/fresh_sample.csv")
OUT = Path("validation/fresh_labels.csv")

NAMES = {
    "1": "lag_performance", "2": "server_connection", "3": "download_open_crash",
    "4": "hackers_cheaters", "5": "pricing_pay2win", "6": "payment_missing_items",
    "7": "matchmaking_balance", "8": "bugs_glitches", "9": "account_ban_loss",
    "10": "content_events_changes", "11": "device_optimization",
    "12": "general_negative", "0": "none",
}

# Labels assigned by Claude (AI-assisted), keyed by row number in fresh_sample.csv
L = {
0:"7", 1:"12", 2:"9", 3:"1,11", 4:"10", 5:"12", 6:"10", 7:"10", 8:"3", 9:"0",
10:"4", 11:"8", 12:"0", 13:"1", 14:"4", 15:"9", 16:"5", 17:"9", 18:"8,12", 19:"0",
20:"0", 21:"10", 22:"5", 23:"1,8", 24:"8", 25:"12", 26:"2", 27:"5,8,10", 28:"2,3", 29:"4,8",
30:"10", 31:"7", 32:"0", 33:"3", 34:"2", 35:"1,11", 36:"2", 37:"8,12", 38:"0", 39:"3",
40:"1", 41:"9", 42:"12", 43:"7", 44:"0", 45:"0", 46:"1,2", 47:"9", 48:"10", 49:"6",
50:"7", 51:"12", 52:"12", 53:"0", 54:"0", 55:"11", 56:"4,9", 57:"0", 58:"12", 59:"7,10",
60:"7,12", 61:"0", 62:"1,11", 63:"0", 64:"1,3", 65:"12", 66:"7", 67:"12", 68:"7,10", 69:"0",
70:"1,11", 71:"0", 72:"12", 73:"12", 74:"0", 75:"12", 76:"12", 77:"3", 78:"7,10", 79:"2,10",
80:"5,9", 81:"0", 82:"12", 83:"1,11", 84:"4,5", 85:"7,10", 86:"7", 87:"7", 88:"10", 89:"8",
90:"0", 91:"10", 92:"7", 93:"12", 94:"7,10", 95:"7,10", 96:"4", 97:"5", 98:"10", 99:"3,8",
100:"0", 101:"10", 102:"10", 103:"0", 104:"0", 105:"0", 106:"12", 107:"6", 108:"10", 109:"0",
110:"5", 111:"0", 112:"1,2", 113:"3", 114:"0", 115:"0", 116:"10", 117:"5", 118:"1,2,8", 119:"12",
}

sample = pd.read_csv(SAMPLE)
assert len(sample) == 120, "fresh_sample.csv should have 120 rows"

CHECKS = {0: "só merece 5", 4: "Please bring back old", 60: "gamenya jelek",
          107: "paguei meus diamantes", 119: "birokti kor"}
for i, start in CHECKS.items():
    got = " ".join(str(sample.loc[i, "content"]).split())
    assert got.startswith(start), f"row {i} does not match, tell Claude"

OUT.parent.mkdir(exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["review_id", "language", "true_labels", "labelled_by"])
    for i, row in sample.iterrows():
        codes = [c.strip() for c in L[i].split(",")]
        names = "|".join(sorted({NAMES[c] for c in codes}))
        writer.writerow([row.review_id, row.language, names, "claude_ai_assisted"])

print("Wrote", len(sample), "labels to", OUT)
