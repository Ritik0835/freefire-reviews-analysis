import re
import unicodedata
from pathlib import Path

import pandas as pd

IN_FILE = Path("data/clean_reviews.csv")
OUT_FILE = Path("data/categorized_reviews.csv")

# "words": whole-word matches (Latin script, lowercase, phrases allowed)
# "native": Devanagari substrings, also matched with spaces removed
CATEGORIES = {
    "lag_performance": {
        "words": ["lag", "laggy", "lagging", "leg", "ping", "latency", "freeze",
                  "freezes", "freezing", "frozen", "stutter", "fps", "hang", "hangs",
                  "hanging", "hang ho", "lento", "lenta", "travando", "trava", "travar",
                  "travação", "travacao", "gela", "gelando", "congela", "lemot",
                  "ngelag", "patah", "loading", "carregando", "carrega", "slow"],
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
                  "not working", "doesn't work", "does not work", "not loading",
                  "baixar", "instalar", "não abre", "nao abre", "unduh",
                  "tidak bisa dibuka", "gabisa dibuka", "chalu nahi", "chalu nahin",
                  "open nahi", "nahi chalta", "nahin chalta", "nahi chal", "nahin chal",
                  "chal nahi", "khul nahi", "nahi khul", "download nahi"],
        "native": ["डाउनलोड", "इंस्टॉल", "लॉगिन", "चालू नहीं", "चलता नहीं", "ओपन नहीं",
                   "चल नहीं", "नहीं चल"],
    },
    "hackers_cheaters": {
        "words": ["hack", "hacks", "hacker", "hackers", "hacking", "cheat", "cheater",
                  "cheaters", "cheating", "aimbot", "wallhack", "trapaça",
                  "trapaceiros"],
        "native": ["हैकर", "चीटर", "हैक", "चीट"],
    },
    "pricing_pay2win": {
        "words": ["pay to win", "p2w", "pay2win", "expensive", "overpriced", "costly",
                  "price", "prices", "greedy", "greed", "scam", "money", "bundle",
                  "spin", "spins", "mahal", "harga", "bundel", "kikir", "preço",
                  "preços", "preco", "precos", "caro", "caros", "ganância", "ganancia",
                  "dinheiro", "giros", "paise", "paisa", "mehnga", "mehenga", "mahanga"],
        "native": ["महंगा", "पैसे", "पैसा"],
    },
    "payment_missing_items": {
        "words": ["top up", "topup", "top-up", "diamond", "diamonds", "diamante",
                  "diamantes", "not received", "didn't receive", "not credited",
                  "refund", "payment", "purchase", "charged", "recharge", "recarga",
                  "pagamento", "reembolso", "tidak masuk", "belum masuk", "gak masuk",
                  "ga masuk", "nahi mila", "nhi mila"],
        "native": ["डायमंड", "टॉप अप", "रिचार्ज", "रिफंड", "नहीं मिला"],
    },
    "matchmaking_balance": {
        "words": ["matchmaking", "teammate", "teammates", "team mate", "team mates",
                  "random team", "tim beban", "beban", "bots", "bot", "noob", "noobs",
                  "unfair", "unbalanced", "balance", "balanceamento", "nerf", "nerfed",
                  "overpowered", "damage", "aim", "mira", "dano", "armas", "personagem",
                  "partida", "lawan", "musuh"],
        "native": ["नूब", "मैचमेकिंग", "बॉट"],
    },
    "bugs_glitches": {
        "words": ["bug", "bugs", "buggy", "glitch", "glitches", "error", "errors",
                  "eror", "bugado", "erro", "erros", "gabisa", "gak bisa", "ga bisa",
                  "tidak bisa", "nggak bisa", "enggak bisa"],
        "native": ["बग", "ग्लिच", "प्रॉब्लम"],
    },
    "account_ban_loss": {
        "words": ["account", "accounts", "banned", "ban", "suspended", "suspend",
                  "my id", "id ban", "id band", "id lost", "id deleted", "akun",
                  "blokir", "conta", "banida", "banido", "hilang"],
        "native": ["आईडी", "अकाउंट", "बैन"],
    },
    "content_events_changes": {
        "words": ["event", "events", "old free fire", "old version", "old peak",
                  "old map", "old days", "old graphics", "bring back", "return old",
                  "removed", "remove", "revival", "update", "updates", "patch",
                  "evento", "eventos", "atualização", "atualizacao", "antigamente",
                  "versão antiga", "versao antiga", "versi lama", "purana", "purani",
                  "wapas", "vapas", "mapa", "mapas", "maps"],
        "native": ["अपडेट", "पुराना", "वापस"],
    },
    "device_optimization": {
        "words": ["optimize", "optimized", "optimization", "x86", "emulator",
                  "device", "heating", "overheat", "battery", "storage", "memory",
                  "low end", "low-end", "celular", "aparelho", "esquenta",
                  "otimização", "otimizado", "armazenamento", "memória", "memori",
                  "panas", "ram"],
        "native": ["बैटरी", "गर्म"],
    },
    "general_negative": {
        "words": ["worst", "boring", "bad", "trash", "waste", "useless", "fazool",
                  "bakwas", "ganda", "kharab", "ghatiya", "pathetic", "ruim",
                  "horrível", "horrivel", "chato", "jelek", "buruk", "sampah",
                  "gak seru", "tidak seru", "not fun", "garbage", "terrible",
                  "horrible", "disappointed", "disappointing", "hate", "pointless",
                  "stupid", "fraud", "fake", "farji", "ruined", "estragou", "lixo"],
        "native": ["बकवास", "खराब", "घटिया", "बेकार", "फालतू", "बोरिंग", "गंदा"],
    },
}

GENERAL = "general_negative"
SPECIFIC = [c for c in CATEGORIES if c != GENERAL]


def normalize(s):
    s = unicodedata.normalize("NFC", s.lower())
    return re.sub(r"[\u200b-\u200d\ufeff]", "", s)


def compile_category(cfg):
    words = sorted(cfg["words"], key=len, reverse=True)
    pattern = re.compile(r"\b(?:" + "|".join(re.escape(w) for w in words) + r")\b")
    return pattern, cfg["native"]


PATTERNS = {name: compile_category(cfg) for name, cfg in CATEGORIES.items()}


def matches(t, t_nospace, pattern, native):
    if pattern.search(t):
        return True
    return any(n.replace(" ", "") in t_nospace for n in native)


df = pd.read_csv(IN_FILE)
df["content"] = df["content"].fillna("").astype(str)
text = df["content"].apply(normalize)
text_ns = text.apply(lambda s: re.sub(r"\s+", "", s))

for name, (pattern, native) in PATTERNS.items():
    df[name] = [matches(t, ns, pattern, native) for t, ns in zip(text, text_ns)]

df["n_specific"] = df[SPECIFIC].sum(axis=1)
df["category_status"] = "uncategorized"
df.loc[df["content_length"] < 10, "category_status"] = "too_short"
df.loc[df[GENERAL], "category_status"] = "general_only"
df.loc[df["n_specific"] > 0, "category_status"] = "categorized"

df.to_csv(OUT_FILE, index=False)

neg = df[df["rating_group"] == "negative"]
long_neg = neg[neg["content_length"] >= 25]

print("\nNegative reviews: status (%)")
print(neg["category_status"].value_counts(normalize=True).mul(100).round(1))

print("\nNegative reviews with 25+ characters: status (%)")
print(long_neg["category_status"].value_counts(normalize=True).mul(100).round(1))

print("\nShare of negative reviews matching each category (%)")
cols = SPECIFIC + [GENERAL]
summary = pd.DataFrame({
    "reviews": neg[cols].sum(),
    "pct_of_negative": neg[cols].mean().mul(100).round(1),
}).sort_values("pct_of_negative", ascending=False)
print(summary)

print("\nBy language market (% of negative reviews)")
print(neg.groupby("language")[cols].mean().mul(100).round(1).T)
