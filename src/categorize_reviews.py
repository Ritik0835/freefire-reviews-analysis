import re
from pathlib import Path

import pandas as pd

IN_FILE = Path("data/clean_reviews.csv")
OUT_FILE = Path("data/categorized_reviews.csv")

# "words" are matched as whole words (Latin script, lowercase).
# "native" are matched as plain substrings (Devanagari).
CATEGORIES = {
    "lag_performance": {
        "words": ["lag", "laggy", "lagging", "leg", "ping", "latency", "freeze",
                  "freezes", "freezing", "frozen", "stutter", "fps", "hang", "hangs",
                  "lento", "lenta", "travando", "trava", "travar", "gela", "gelando",
                  "congela", "lemot", "ngelag", "patah", "loading", "slow"],
        "native": ["लैग", "लेग", "हैंग", "पिंग"],
    },
    "server_connection": {
        "words": ["server", "servers", "network", "connection", "disconnect",
                  "disconnects", "internet", "wifi", "sinyal", "jaringan",
                  "conexão", "conexao", "rede", "servidor"],
        "native": ["सर्वर", "नेटवर्क", "कनेक्शन"],
    },
    "download_open_crash": {
        "words": ["download", "install", "login", "crash", "crashes", "crashing",
                  "force close", "not opening", "won't open", "cant open", "can't open",
                  "baixar", "instalar", "não abre", "nao abre", "unduh",
                  "tidak bisa dibuka", "gabisa dibuka", "chalu nahi", "chalu nahin",
                  "open nahi", "nahi chalta", "nahin chalta", "download nahi"],
        "native": ["डाउनलोड", "इंस्टॉल", "लॉगिन", "चालू नहीं", "चलता नहीं", "ओपन नहीं"],
    },
    "hackers_cheaters": {
        "words": ["hack", "hacks", "hacker", "hackers", "hacking", "cheat", "cheater",
                  "cheaters", "cheating", "aimbot", "wallhack", "trapaça",
                  "trapaceiros"],
        "native": ["हैकर", "चीटर", "हैक"],
    },
    "pricing_pay2win": {
        "words": ["pay to win", "p2w", "pay2win", "expensive", "overpriced", "price",
                  "prices", "greedy", "scam", "money", "bundle", "spin", "spins",
                  "mahal", "harga", "bundel", "kikir", "preço", "preços", "preco",
                  "precos", "caro", "dinheiro", "giros"],
        "native": ["महंगा", "पैसे"],
    },
    "payment_missing_items": {
        "words": ["top up", "topup", "top-up", "diamond", "diamonds", "not received",
                  "didn't receive", "not credited", "refund", "payment", "purchase",
                  "charged", "recharge", "tidak masuk", "belum masuk"],
        "native": ["डायमंड", "टॉप अप", "रिचार्ज", "रिफंड"],
    },
    "matchmaking_balance": {
        "words": ["matchmaking", "teammate", "teammates", "random team", "tim beban",
                  "beban", "bots", "bot", "unfair", "unbalanced", "balance", "nerf",
                  "nerfed", "damage", "aim", "mira", "dano"],
        "native": [],
    },
    "bugs_glitches": {
        "words": ["bug", "bugs", "buggy", "glitch", "glitches", "error", "errors",
                  "eror", "bugado", "erro", "erros"],
        "native": ["बग"],
    },
    "content_events_changes": {
        "words": ["event", "events", "old", "miss", "bring back", "removed",
                  "update", "updates", "evento", "eventos", "atualização",
                  "atualizacao", "versão antiga", "versi lama", "dihapus",
                  "hapus", "purana", "wapas"],
        "native": ["अपडेट", "पुराना", "वापस"],
    },
    "device_optimization": {
        "words": ["optimize", "optimized", "optimization", "x86", "emulator",
                  "device", "heating", "overheat", "battery", "storage", "memory",
                  "low end", "low-end", "celular", "aparelho", "esquenta",
                  "otimização", "otimizado", "armazenamento", "memória", "memori",
                  "panas"],
        "native": ["बैटरी", "गर्म"],
    },
}


def compile_category(cfg):
    words = sorted(cfg["words"], key=len, reverse=True)
    pattern = re.compile(r"\b(?:" + "|".join(re.escape(w) for w in words) + r")\b")
    return pattern, cfg["native"]


PATTERNS = {name: compile_category(cfg) for name, cfg in CATEGORIES.items()}


def matches(text, pattern, native):
    return bool(pattern.search(text)) or any(n in text for n in native)


df = pd.read_csv(IN_FILE)
df["content"] = df["content"].fillna("").astype(str)
text = df["content"].str.lower()

cat_cols = list(CATEGORIES)
for name, (pattern, native) in PATTERNS.items():
    df[name] = text.apply(lambda t: matches(t, pattern, native))

df["n_categories"] = df[cat_cols].sum(axis=1)
df["category_status"] = "uncategorized"
df.loc[df["content_length"] < 10, "category_status"] = "too_short"
df.loc[df["n_categories"] > 0, "category_status"] = "categorized"

df.to_csv(OUT_FILE, index=False)

neg = df[df["rating_group"] == "negative"]

print("\nNegative reviews: category status (%)")
print(neg["category_status"].value_counts(normalize=True).mul(100).round(1))

print("\nShare of negative reviews matching each category (%)")
summary = pd.DataFrame({
    "reviews": neg[cat_cols].sum(),
    "pct_of_negative": neg[cat_cols].mean().mul(100).round(1),
}).sort_values("pct_of_negative", ascending=False)
print(summary)

print("\nBy language market (% of negative reviews)")
print(neg.groupby("language")[cat_cols].mean().mul(100).round(1).T)
