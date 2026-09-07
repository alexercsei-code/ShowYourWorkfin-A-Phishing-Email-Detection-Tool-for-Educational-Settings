"""features.py - turns raw email text into the inputs the phishing model needs.

Used by notebook 04 (training_models), notebook 05 (evaluation) and the tool.
"""
import re
import pandas as pd

# ---- words that suggest urgency, credential requests, or money -------------
# These lists come from NCSC guidance on recognising phishing and from the
# literature review. They are counted, not removed.
URGENCY_WORDS = [
    "urgent", "urgently", "immediately", "immediate", "now", "asap", "expire", "expires",
    "expired", "expiring", "suspended", "suspend", "deadline", "final notice", "last chance",
    "within 24 hours", "within 48 hours", "action required", "act now", "warning", "alert",
    "limited time", "today only", "failure to", "will be closed", "will be locked",
]
CREDENTIAL_WORDS = [
    "password", "passcode", "login", "log in", "sign in", "username", "verify", "verification",
    "confirm", "confirmation", "authenticate", "credentials", "account", "security",
    "update your", "validate", "re-activate", "reactivate", "unlock", "mailbox", "quota",
]
MONEY_WORDS = [
    "payment", "invoice", "bank", "transfer", "refund", "£", "$", "€", "usd", "gbp",
    "fund", "funds", "wire", "bitcoin", "gift card", "voucher", "salary", "payroll",
    "tax", "hmrc", "paypal", "purchase", "order", "prize", "lottery", "won",
]

def _count_any(text_lower, words):
    """How many times any of the words appear in the text."""
    return sum(text_lower.count(w) for w in words)


def clean_text(text):
    """Same cleaning as notebook 03, so the model sees the same style of text."""
    text = str(text)
    text = re.sub(r"<[^>]+>", " ", text)                                   # HTML tags
    text = re.sub(r"^(message-id|x-[\w-]+|received|content-type|content-transfer-encoding|"
                  r"mime-version|return-path|delivered-to|list-id|precedence|in-reply-to|"
                  r"references|sender|reply-to|date|to|cc|bcc|from):.*$",
                  " ", text, flags=re.IGNORECASE | re.MULTILINE)           # header lines
    text = re.sub(r"(https?://\S+|www\.\S+)", " URL ", text)               # links
    text = re.sub(r"\S+@\S+", " EMAIL ", text)                             # email addresses
    text = re.sub(r"\d{5,}", " NUMBER ", text)                             # long numbers
    text = re.sub(r"\b(19[9]\d|20[0-2]\d)\b", " YEAR ", text)              # years
    text = re.sub(r"[^\w\s!?$%£€.,:;'\"()\-]", " ", text)                  # odd characters
    text = re.sub(r"\s+", " ", text).strip()
    return text


def structural_features(text):
    """Counts and ratios from the ORIGINAL email text. Returns a dictionary."""
    text = str(text)
    lower = text.lower()
    letters = [c for c in text if c.isalpha()]
    n_letters = max(len(letters), 1)                  # max(...,1) avoids dividing by zero
    words = text.split()
    n_words = max(len(words), 1)

    urls = re.findall(r"(https?://\S+|www\.\S+)", text)
    return {
        "n_chars":        len(text),
        "n_words":        len(words),
        "n_urls":         len(urls),
        "n_emails":       len(re.findall(r"\S+@\S+", text)),
        "n_exclaim":      text.count("!"),
        "n_question":     text.count("?"),
        "caps_ratio":     sum(1 for c in letters if c.isupper()) / n_letters,
        "digit_ratio":    sum(1 for c in text if c.isdigit()) / max(len(text), 1),
        "n_urgency":      _count_any(lower, URGENCY_WORDS),
        "n_credential":   _count_any(lower, CREDENTIAL_WORDS),
        "n_money":        _count_any(lower, MONEY_WORDS),
        "has_ip_url":     int(bool(re.search(r"https?://\d{1,3}(\.\d{1,3}){3}", text))),
        "avg_word_len":   sum(len(w) for w in words) / n_words,
    }

STRUCTURAL_COLUMNS = list(structural_features("example").keys())


def make_frame(raw_texts, clean_texts=None):
    """Build the table the model expects: one 'text_clean' column plus the
    structural feature columns. If clean_texts is not given, clean_text() is used."""
    raw_texts = list(raw_texts)
    if clean_texts is None:
        clean_texts = [clean_text(t) for t in raw_texts]
    frame = pd.DataFrame([structural_features(t) for t in raw_texts])
    frame.insert(0, "text_clean", list(clean_texts))
    return frame
