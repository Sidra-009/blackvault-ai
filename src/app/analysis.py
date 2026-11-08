"""Rule-based helpers (no machine learning, no network access). They sit next to the ML model and explain a message."""
import re

# (key, regex). Matched on lower-cased text.
FLAG_PATTERNS = [
    ("urgency", r"foran|jaldi|urgent|immediately|right now|asap|today|aaj raat|last chance|within \d+ (hours?|minutes?)"),
    ("link", r"https?://|www\.|bit\.ly|\.xyz\b|\.top\b"),
    ("cred", r"\botp\b|\bpin\b|password|\bcvv\b|\bcnic\b|verification code|passcode"),
    ("money", r"\bpay\b|\bfee\b|send money|transfer|easypaisa|jazzcash|\brs\.? ?\d|rupees|\bprize\b|lottery|inam"),
    ("org", r"\bbank\b|nadra|\bfbr\b|police|\bfia\b|courier|\bdhl\b|\btcs\b|\baccount\b"),
    ("threat", r"\bblock|suspend|band ho|legal action|arrest|congratulations|\bwinner\b|you won|jeet"),
]

TYPE_PATTERNS = [
    ("parcel", r"parcel|courier|delivery|package|shipment|\bdhl\b|\btcs\b|leopards|customs"),
    ("prize", r"prize|lottery|congratulations|you won|winner|\binam|\bjeet|lucky draw|\bbisp\b|ehsaas"),
    ("invest", r"invest|profit|double your|daily income|work from home|job offer|part[- ]time|crypto|trading"),
    ("authority", r"\bbill\b|k-?electric|sui gas|\bptcl\b|\bfbr\b|\bnadra\b|police|\bfia\b|court|notice|disconnect|sim (will be )?block"),
]

URL_RE = re.compile(
    r"(?:https?://|www\.)[^\s<>\"']+|\b(?:bit\.ly|tinyurl\.com|t\.co|goo\.gl|cutt\.ly|is\.gd|rb\.gy)/[^\s<>\"']+",
    re.IGNORECASE,
)
PHONE_RE = re.compile(r"(?<!\d)(?:\+92|0092|92|0)[\s-]?3\d{2}[\s-]?\d{7}(?!\d)")
AMOUNT_RE = re.compile(r"\b(?:rs\.?|pkr|rupees?)\s?\d[\d,]*|\b\d[\d,]*\s?(?:rs\b|rupees?\b|pkr\b)", re.IGNORECASE)

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "cutt.ly", "is.gd", "rb.gy"}
ODD_TLDS = (".xyz", ".top", ".click", ".link", ".live", ".icu", ".cfd", ".sbs", ".support", ".monster", ".rest", ".cyou")
LURE_WORDS = ("verify", "secure", "login", "signin", "update", "account", "bank", "wallet", "easypaisa", "jazzcash",
              "hbl", "ubl", "mcb", "meezan", "nadra", "fbr", "ptcl", "refund", "claim", "reward", "prize", "track", "parcel")


def find_flags(text):
    low = text.lower()
    return [k for k, pat in FLAG_PATTERNS if re.search(pat, low)]


def scam_types(text, flags):
    low = text.lower()
    found = []
    if "cred" in flags and ("org" in flags or "threat" in flags):
        found.append("bank")
    for key, pat in TYPE_PATTERNS:
        if re.search(pat, low):
            found.append(key)
    return found[:2]


def extract_urls(text):
    seen, out = set(), []
    for m in URL_RE.finditer(text):
        u = m.group(0).rstrip(".,;:!?)\"'")
        if u.lower() not in seen:
            seen.add(u.lower())
            out.append(u)
    return out


def analyze_url(raw):
    """Offline checks of the link text only. We never open the link."""
    low = raw.lower()
    issues = []
    if low.startswith("http://"):
        issues.append("no_https")
    rest = re.sub(r"^https?://", "", low)
    authority = re.split(r"[/?#]", rest)[0]
    if "@" in authority:
        issues.append("at_sign")
    host = authority.split("@")[-1].split(":")[0]
    if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host):
        issues.append("ip_host")
    if host in SHORTENERS:
        issues.append("shortener")
    if host.endswith(ODD_TLDS):
        issues.append("odd_tld")
    if "xn--" in host:
        issues.append("punycode")
    if host.count("-") >= 2 or len(host) > 35:
        issues.append("long_host")
    if "-" in host and any(w in host for w in LURE_WORDS):
        issues.append("lookalike")
    return {"url": raw, "host": host, "issues": issues}


def extract_entities(text):
    phones = list(dict.fromkeys(m.group(0).strip() for m in PHONE_RE.finditer(text)))
    amounts = list(dict.fromkeys(m.group(0).strip() for m in AMOUNT_RE.finditer(text)))
    return {"phones": phones, "amounts": amounts}


def final_verdict(risk, flags, url_reports):
    """Return (color, verdict_key, basis). The 35% / 65% model cut-offs and the rule overrides are demo choices."""
    if risk >= 0.65:
        color, key = "red", "red"
    elif risk >= 0.35:
        color, key = "amber", "amber"
    else:
        color, key = "green", "green"

    secret_ask = "cred" in flags and any(k in flags for k in ("link", "urgency", "money"))
    risky_url = any(
        len(r["issues"]) >= 2 or any(i in r["issues"] for i in ("ip_host", "punycode", "at_sign"))
        for r in url_reports
    )
    if secret_ask and risky_url:
        return "red", "red_rules", "rules"
    if color == "green" and (secret_ask or risky_url or len(flags) >= 3):
        return "amber", "amber_rules", "rules"
    return color, key, "model"
