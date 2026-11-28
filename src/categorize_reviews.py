import re
import unicodedata
from pathlib import Path

import pandas as pd

IN_FILE = Path("data/clean_reviews.csv")
OUT_FILE = Path("data/categorized_reviews.csv")

# Each category has:
#   words / native : STRONG keywords (always count)
#   weak / weak_native : counted only if the review matched no strong keyword anywhere
#   ignore : regex patterns deleted from the text before matching this category
# "words" are whole-word matches (Latin script); "native" are Devanagari strings.
CATEGORIES = {
    "lag_performance": {
        "words": ["lag", "laggy", "lagging", "lagged", "lagado", "lagada", "lagou",
                  "lage", "lagy", "leggy", "leg", "ping", "latency", "freeze", "freezes",
                  "freezing", "frozen", "stutter", "stuttering", "fps", "hang", "hangs",
                  "hanging", "hang ho", "heg", "delay", "delays", "lento", "lenta",
                  "travando", "trava", "travar", "travação", "travacao", "gela",
                  "gelando", "congela", "lemot", "ngelag", "ngeleg", "ngelek", "patah",
                  "slow", "slowly", "sluggish", "silo", "loading", "carregando",
                  "carrega", "performa", "performance", "rack", "net lagta"],
        "native": ["लैग", "लेग", "हैंग", "हेग", "पिंग", "स्लो"],
    },
    "server_connection": {
        "words": ["server", "servers", "servidor", "servidores", "sarvar", "sarver",
                  "network", "connection", "conexão", "conexao", "reconnect",
                  "reconectar", "disconnect", "disconnects", "disconnected", "internet",
                  "wifi", "sinyal", "jaringan", "rede"],
        "native": ["सर्वर", "नेटवर्क", "कनेक्शन"],
        "ignore": [
            r"jaringan\s+(?:\w+\s+){0,2}?(?:bagus\w*|lancar|stabil|normal)",
            r"sinyal\s+(?:\w+\s+){0,2}?(?:bagus\w*|lancar)",
            r"(?:wifi|internet|kuota)\s+(?:\w+\s+){0,2}?(?:bagus\w*|lancar)",
            r"(?:network|internet|connection|wifi)\s+(?:is\s+)?(?:good|fine|stable)",
            r"(?:rede|internet|conex[aã]o)\s+(?:est[aá]\s+|ta\s+)?(?:boa|normal|ok|est[aá]vel)",
        ],
    },
    "download_open_crash": {
        "words": ["download", "install", "crash", "crashes", "crashing", "force close",
                  "not opening", "won't open", "cant open", "can't open", "open nahi",
                  "open nahin", "open nhi", "open hote", "login nahi", "login nhi",
                  "log in nahi", "nahi chalta", "nahin chalta", "chalu nahi",
                  "chalu nahin", "nahi khul", "khul nahi", "download nahi", "baixar",
                  "instalar", "não abre", "nao abre", "não consigo entrar",
                  "nao consigo entrar", "não entra", "nao entra", "não está entrando",
                  "nao esta entrando", "fica saindo", "saindo do nada", "unduh",
                  "tidak bisa dibuka", "gabisa dibuka", "tidak bisa masuk",
                  "gak bisa masuk", "gabisa masuk", "ga bisa masuk", "gak bisa login",
                  "gabisa login", "ga bisa login", "tidak bisa login", "terpental",
                  "update nahi", "update nhi"],
        "native": ["डाउनलोड", "इंस्टॉल", "लॉगिन", "चालू नहीं", "चलता नहीं", "ओपन नहीं",
                   "लोग ईन", "लोग इन", "अपडेट नहीं हो", "अपडेट नही हो"],
        "weak": ["login", "not working", "doesn't work", "does not work", "not loading",
                 "nahi chal raha", "nahi chal rahi", "nahin chal raha", "nhi chal raha",
                 "nahi chal", "chal nahi", "nahin chal"],
        "weak_native": ["नहीं चल", "नही चल", "चल नहीं", "चल नही"],
        "ignore": [
            r"(?:don'?t|do not|dont|never)\s+(?:ever\s+)?(?:download|install)",
            r"n[aã]o\s+baixe",
            r"jangan\s+(?:di)?(?:download|unduh|install)",
        ],
    },
    "hackers_cheaters": {
        "words": ["hack", "hacks", "hacker", "hackers", "hacking", "hackeado", "hackear",
                  "cheat", "cheater", "cheaters", "cheating", "chet", "xiter", "xiters",
                  "aimbot", "wallhack", "panel", "pirates", "pirate", "piratas",
                  "trapaça", "trapaceiros"],
        "native": ["हैकर", "हैकिंग", "चीटर"],
        "ignore": [
            r"(?:never|not|didn'?t|don'?t|do not|dont)\s+(?:ever\s+)?(?:use|used|using)\s+(?:any\s+)?(?:3rd-party\s+apps?\s+to\s+)?(?:hacks?|cheats?|cheating)",
            r"\bto\s+hack\s+the\s+game",
            r"(?:kaga|gak|ga|tidak|nggak|ngga|enggak)\s+(?:make|makai|pake|pakai|pakek|memakai)\s+(?:cheat|chet|hack)\w*",
            r"nunca\s+usei\s+(?:hack|cheat)\w*",
        ],
    },
    "pricing_pay2win": {
        "words": ["pay to win", "p2w", "pay2win", "expensive", "overpriced", "costly",
                  "price", "prices", "greedy", "greed", "scam", "money", "bundle",
                  "spin", "spins", "mahal", "harga", "bundel", "kikir", "preço",
                  "preços", "preco", "precos", "caro", "caros", "ganância", "ganancia",
                  "dinheiro", "giros", "paise", "paisa", "pese", "pesa", "pasie",
                  "mehnge", "mehnga", "mehenga", "mahanga"],
        "native": ["महंगा", "महंगे", "पैसे", "पैसा", "ज्यादा लगते"],
    },
    "payment_missing_items": {
        "words": ["not received", "didn't receive", "not credited", "refund", "reembolso",
                  "payment", "pagamento", "pembayaran", "recarga", "recharge",
                  "tidak masuk", "belum masuk", "gak masuk", "ga masuk", "ngga masuk",
                  "nggak masuk", "belum datang", "balum datang", "nahi mila", "nhi mila",
                  "não chegou", "nao chegou", "não chegaram", "nao chegaram",
                  "não recebi", "nao recebi", "top up nhi", "top up nahi", "top up not",
                  "topup nahi", "topup not"],
        "native": ["नहीं मिला", "नही मिला", "रिचार्ज", "रिफंड", "टॉप अप नहीं"],
    },
    "matchmaking_balance": {
        "words": ["matchmaking", "match making", "teammate", "teammates", "team mate",
                  "team mates", "random team", "tim beban", "beban", "bots", "bot",
                  "noob", "noobs", "unfair", "unbalanced", "balance", "balanceamento",
                  "desbalanceado", "desbalanceada", "desbalanceados", "desbalanceadas",
                  "nerf", "nerfed", "buff", "overpowered", "too strong", "muito forte",
                  "muito fortes", "roubada", "roubadas", "roubado", "roubados", "poder",
                  "poderes", "power", "skorp", "scorp", "armas novas", "novas armas",
                  "habilidade", "habilidades", "abilidade", "abilidades", "tim jelek",
                  "tim sampah", "tim busuk", "tim bot", "temen kroco", "teman kroco",
                  "kroco", "temen bot", "teman bot", "dongo", "pencarian squad",
                  "sistem pencarian", "bocil", "troll", "trol", "toxic", "toksix",
                  "no helpful", "unsupportive", "afk", "perlindungan", "protection",
                  "patente", "patentes"],
        "native": ["नूब", "मैचमेकिंग", "बॉट"],
        "weak": ["personagem", "personagens"],
    },
    "bugs_glitches": {
        "words": ["bug", "bugs", "buggy", "glitch", "glitches", "bugado", "erro", "erros"],
        "native": ["बग", "ग्लिच"],
        "weak": ["error", "errors", "eror", "gabisa", "gak bisa", "ga bisa", "tidak bisa",
                 "nggak bisa", "enggak bisa", "problem", "problems"],
        "weak_native": ["प्रॉब्लम"],
    },
    "account_ban_loss": {
        "words": ["account", "accounts", "banned", "banimento", "banido", "banida",
                  "bandida", "bandido", "banidos", "ban", "suspended", "suspend",
                  "suspenso", "suspensa", "my id", "id ban", "id band", "id lost",
                  "id deleted", "akun", "blokir", "conta foi", "conta banida",
                  "conta bandida", "conta suspensa", "minha conta foi", "hilang",
                  "kena ban", "kena band", "kena bl", "kenah bl", "di band", "dibanned",
                  "dibaned"],
        "native": ["आईडी", "अकाउंट", "बैन"],
        "ignore": [
            r"\bban(?:ned|ning)?\s+(?:all\s+|the\s+|these\s+|those\s+)?(?:hackers?|cheaters?|panel\w*|this game|them|devices?|dvice)",
            r"(?:not|never|nobody|no)\s+(?:get\s+|got\s+|being\s+)?ban(?:ned)?\b",
            r"n[aã]o\s+tomam\s+banimento",
            r"(?:gk|gak|ga|kaga|nggak|ngga|tidak|belum)\s+(?:di\s*)?ban(?:d|ned|ed)?\b",
        ],
    },
    "content_events_changes": {
        "words": ["event", "events", "evento", "eventos", "old free fire", "old ff",
                  "old version", "old peak", "old pick", "old pic", "old map",
                  "old lobby", "old days", "old graphics", "bring back", "return old",
                  "not return", "removed", "remove", "removido", "removeram", "revival",
                  "free fire india", "freefire india", "ff india", "india version",
                  "mapa", "mapas", "map", "maps", "antigamente", "antigas", "antiga",
                  "antigo", "versão antiga", "versao antiga", "versi lama",
                  "melhor antes", "era melhor", "take a break", "break system",
                  "time limit", "hud", "sensifitas", "comeback", "back jump",
                  "add more", "não escuta a comunidade", "ninguém pediu",
                  "coisas desnecessárias", "purana", "purani", "wapas", "vapas",
                  "peak", "peck"],
        "native": ["पुराना", "वापस", "पिक", "पीक", "ओल्ड"],
        "weak": ["update", "updates", "upadate", "upadare", "abdet", "apdet",
                 "atualização", "atualizacao", "atualizações", "patch"],
        "weak_native": ["अपडेट"],
    },
    "device_optimization": {
        "words": ["optimize", "optimized", "optimization", "otimização", "otimizado",
                  "otimizacao", "x86", "emulator", "device", "heating", "overheat",
                  "battery", "storage", "memory", "memori", "ram", "hp", "chromebook",
                  "realme", "redmi", "samsung", "xiaomi", "poco", "iphone", "low end",
                  "low-end", "celular", "aparelho", "esquenta", "armazenamento",
                  "memória", "panas", "pesado", "pesada", "berat", "heavy",
                  "better graphics", "high graphics"],
        "native": ["बैटरी", "गर्म", "स्टोरेज"],
        "weak": ["phone", "phones", "mobile", "mobail", "gb"],
        "weak_native": ["फोन", "मोबाइल", "जीबी"],
        "ignore": [r"\bhp\s+(?:\w+\s+)?bagus", r"\b(?:good|great)\s+phone"],
    },
}

# Counted only if the review matched no specific category at all
GENERAL = {
    "words": ["worst", "worsts", "boring", "bad", "poor", "average", "trash", "waste",
              "useless", "fazool", "bakwas", "bakvash", "bekar", "bekaar", "ganda",
              "kharab", "ghatiya", "pathetic", "ruim", "horrível", "horrivel", "chato",
              "enjoativo", "estressante", "feia", "jelek", "buruk", "burik", "rusak",
              "sampah", "membosankan", "gak seru", "tidak seru", "ga seru", "gak jelas",
              "ga jelas", "gk jelas", "makin ke sini", "makin sini", "semakin parah",
              "ga layak", "tidak layak", "mending main", "not fun", "garbage",
              "terrible", "horrible", "disappointed", "disappointing", "hate",
              "pointless", "stupid", "fraud", "fake", "farji", "ruined", "estragou",
              "lixo", "mat khele", "mat khelena", "mat khelo", "not good"],
    "native": ["बकवास", "खराब", "घटिया", "बेकार", "फालतू", "बोरिंग", "गंदा",
               "मत खेले", "मत खेलो", "मत खेलें"],
}

GENERAL_NAME = "general_negative"
SPECIFIC = list(CATEGORIES)


def normalize(s):
    s = unicodedata.normalize("NFC", str(s).lower())
    s = s.replace("’", "'").replace("²", " ")
    return re.sub(r"[\u200b-\u200d\ufeff]", "", s)


def word_regex(words):
    words = sorted(set(words), key=len, reverse=True)
    if not words:
        return None
    return re.compile(r"\b(?:" + "|".join(re.escape(w) for w in words) + r")\b")


class Rule:
    def __init__(self, cfg):
        self.strong = word_regex(cfg.get("words", []))
        self.weak = word_regex(cfg.get("weak", []))
        self.native = cfg.get("native", [])
        self.weak_native = cfg.get("weak_native", [])
        self.ignore = [re.compile(p) for p in cfg.get("ignore", [])]

    def prepare(self, t):
        for p in self.ignore:
            t = p.sub(" ", t)
        return t, re.sub(r"\s+", "", t)


def native_hit(n, t, ns):
    k = n.replace(" ", "")
    if len(k) >= 5:  # long keywords also match when spaces are missing or extra
        return n in t or k in ns
    return re.search(r"(?:^|\s)" + re.escape(n), t) is not None  # short: token start


def hit(pattern, native, t, ns):
    if pattern is not None and pattern.search(t):
        return True
    return any(native_hit(n, t, ns) for n in native)


RULES = {name: Rule(cfg) for name, cfg in CATEGORIES.items()}
GENERAL_RULE = Rule(GENERAL)


def categorize(text):
    t0 = normalize(text)
    prepared = {name: rule.prepare(t0) for name, rule in RULES.items()}
    result = {name: hit(rule.strong, rule.native, *prepared[name])
              for name, rule in RULES.items()}
    if not any(result.values()):
        for name, rule in RULES.items():
            if hit(rule.weak, rule.weak_native, *prepared[name]):
                result[name] = True
    if any(result.values()):
        result[GENERAL_NAME] = False
    else:
        result[GENERAL_NAME] = hit(GENERAL_RULE.strong, GENERAL_RULE.native,
                                   t0, re.sub(r"\s+", "", t0))
    return result


def main():
    df = pd.read_csv(IN_FILE)
    df["content"] = df["content"].fillna("").astype(str)
    flags = pd.DataFrame([categorize(t) for t in df["content"]], index=df.index)
    df = pd.concat([df, flags], axis=1)

    cols = SPECIFIC + [GENERAL_NAME]
    df["n_specific"] = df[SPECIFIC].sum(axis=1)
    df["category_status"] = "uncategorized"
    df.loc[df["content_length"] < 10, "category_status"] = "too_short"
    df.loc[df[GENERAL_NAME], "category_status"] = "general_only"
    df.loc[df["n_specific"] > 0, "category_status"] = "categorized"
    df.to_csv(OUT_FILE, index=False)

    neg = df[df["rating_group"] == "negative"]
    long_neg = neg[neg["content_length"] >= 25]

    print("\nNegative reviews: status (%)")
    print(neg["category_status"].value_counts(normalize=True).mul(100).round(1))
    print("\nNegative reviews with 25+ characters: status (%)")
    print(long_neg["category_status"].value_counts(normalize=True).mul(100).round(1))
    print("\nShare of negative reviews matching each category (%)")
    summary = pd.DataFrame({
        "reviews": neg[cols].sum(),
        "pct_of_negative": neg[cols].mean().mul(100).round(1),
    }).sort_values("pct_of_negative", ascending=False)
    print(summary)
    print("\nBy language market (% of negative reviews)")
    print(neg.groupby("language")[cols].mean().mul(100).round(1).T)


if __name__ == "__main__":
    main()
