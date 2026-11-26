import time
from pathlib import Path

import pandas as pd
from google_play_scraper import Sort, reviews

APPS = {
    "freefire": "com.dts.freefireth",
    "freefire_max": "com.dts.freefiremax",
}

# country code -> language code
COUNTRIES = {
    "in": "en",
    "br": "pt",
    "id": "id",
    "us": "en",
}

TARGET_PER_COMBO = 4000   # reviews per app per country
BATCH = 200
OUT_DIR = Path("data/raw")


def scrape(app_name, package, country, lang):
    collected = []
    token = None
    while len(collected) < TARGET_PER_COMBO:
        try:
            batch, token = reviews(
                package,
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=BATCH,
                continuation_token=token,
            )
        except Exception as e:
            print(f"  error: {e}")
            break
        if not batch:
            break
        collected.extend(batch)
        print(f"  {app_name}/{country}: {len(collected)} reviews")
        if token is None:
            break
        time.sleep(1)  # be polite to the server

    df = pd.DataFrame(collected)
    if df.empty:
        print(f"  no data for {app_name}/{country}")
        return
    df["app"] = app_name
    df["country"] = country
    df["lang_requested"] = lang
    df.to_csv(OUT_DIR / f"{app_name}_{country}.csv", index=False)
    print(f"saved {len(df)} rows -> {app_name}_{country}.csv")


if __name__ == "__main__":
    for app_name, package in APPS.items():
        for country, lang in COUNTRIES.items():
            print(f"Scraping {app_name} / {country}")
            scrape(app_name, package, country, lang)
