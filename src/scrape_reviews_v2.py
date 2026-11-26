import time
from pathlib import Path

import pandas as pd
from google_play_scraper import Sort, reviews

APPS = {
    "freefire": "com.dts.freefireth",
    "freefire_max": "com.dts.freefiremax",
}

# (language, country) pairs. We treat these as language markets.
MARKETS = [
    ("en", "us"),
    ("hi", "in"),
    ("pt", "br"),
    ("id", "id"),
]

# reviews to collect per star rating: oversample negatives on purpose
SCORE_TARGET = {1: 2000, 2: 1500, 3: 1500, 4: 1000, 5: 1000}
BATCH = 200
OUT_DIR = Path("data/raw_v2")


def scrape_score(package, lang, country, score, target):
    rows, token = [], None
    while len(rows) < target:
        try:
            batch, token = reviews(
                package,
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=BATCH,
                filter_score_with=score,
                continuation_token=token,
            )
        except Exception as e:
            print(f"    error: {e}")
            break
        if not batch:
            break
        rows.extend(batch)
        if token is None:
            break
        time.sleep(1)
    return rows[:target]


if __name__ == "__main__":
    for app_name, package in APPS.items():
        for lang, country in MARKETS:
            print(f"Scraping {app_name} / {lang}")
            all_rows = []
            for score, target in SCORE_TARGET.items():
                got = scrape_score(package, lang, country, score, target)
                print(f"  score {score}: {len(got)} reviews")
                all_rows.extend(got)

            df = pd.DataFrame(all_rows)
            if df.empty:
                print("  no data")
                continue
            df = df.drop_duplicates(subset="reviewId")
            df["app"] = app_name
            df["language"] = lang
            df.to_csv(OUT_DIR / f"{app_name}_{lang}.csv", index=False)
            print(f"saved {len(df)} rows -> {app_name}_{lang}.csv")
