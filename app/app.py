"""app.py - Show Your Workfin: a phishing email checker for school staff.

Paste the text of an email, get an estimated phishing risk and the reasons
behind it, in plain language. Nothing typed here is stored.

Run with:   streamlit run app.py
Needs:      ../model/phishing_model.joblib and ../Model/features.py
            (copy the Model folder from Google Drive next to the app folder)
"""

import os
import re
import sys

import numpy as np
import streamlit as st


# Where the model lives: the "model" folder next to this file.
try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    HERE = os.getcwd()
MODEL_DIR = os.path.join(HERE, "model")
sys.path.append(MODEL_DIR)

import features  # noqa: E402  (the same features.py used in training)


@st.cache_resource
def load_model():
    """Load the saved model once and keep it in memory."""
    import joblib
    return joblib.load(os.path.join(MODEL_DIR, "phishing_model.joblib"))



# Turning model output into reasons a person can act on

def word_contributions(model, frame, top_n=6):
    """For linear models: which words in THIS email pushed the score up?
    Returns a list of (word, weight). Empty list if the model has no weights."""
    try:
        pipe = model.calibrated_classifiers_[0].estimator
        col_tf = pipe.named_steps["features"]
        clf = pipe.named_steps["model"]
        if not hasattr(clf, "coef_"):
            return []
        vec = col_tf.named_transformers_["tfidf"]
        names = vec.get_feature_names_out()
        n_tfidf = len(names)
        x = col_tf.transform(frame)                # sparse row: tfidf + structural
        x_tfidf = x[:, :n_tfidf].toarray().ravel()
        contrib = x_tfidf * clf.coef_.ravel()[:n_tfidf]
        order = np.argsort(contrib)[::-1]
        out = [(names[i], contrib[i]) for i in order[:top_n] if contrib[i] > 0]
        return out
    except Exception:
        return []


def found_words(text, word_list, limit=4):
    """Which of these words actually appear in the email?"""
    lower = text.lower()
    hits = [w for w in word_list if w in lower]
    return hits[:limit]




# Optional: if the person pasted the full message source (with headers), separate the headers from the body and read the authentication results.

HEADER_LINE = re.compile(r"^[A-Za-z][A-Za-z0-9-]*:\s")

def split_headers(text):
    """Return (headers, body). If the text doesn't start with email headers,
    headers is '' and body is the whole text."""
    lines = text.splitlines()
    if len(lines) < 3 or not HEADER_LINE.match(lines[0]):
        return "", text
    for i, line in enumerate(lines):
        if line.strip() == "":                     # first blank line ends the headers
            return "\n".join(lines[:i]), "\n".join(lines[i + 1:])
    return "", text                                # no blank line: treat as body


def unfold(headers):
    """Header values can wrap onto indented lines; join them back up."""
    return re.sub(r"\r?\n[ \t]+", " ", headers)


def auth_results(headers):
    """Read spf / dkim / dmarc results from an Authentication-Results header.
    Returns a dict like {'spf': 'pass', 'dkim': 'fail', 'dmarc': 'none'} or {}."""
    h = unfold(headers)
    m = re.search(r"^authentication-results:(.*)$", h, flags=re.IGNORECASE | re.MULTILINE)
    if not m:
        return {}
    line = m.group(1).lower()
    out = {}
    for check in ("spf", "dkim", "dmarc"):
        r = re.search(r"\b" + check + r"=([a-z]+)", line)
        if r:
            out[check] = r.group(1)
    return out


def domain_of(value):
    m = re.search(r"@([A-Za-z0-9.-]+)", value or "")
    return m.group(1).lower() if m else None


def header_field(headers, name):
    m = re.search(r"^" + name + r":(.*)$", unfold(headers), flags=re.IGNORECASE | re.MULTILINE)
    return m.group(1).strip() if m else ""


def header_reasons(headers):
    """Plain-language reasons based on the headers. Empty list if none pasted."""
    if not headers:
        return []
    reasons = []
    auth = auth_results(headers)
    if auth:
        failed = [k.upper() for k, v in auth.items() if v in ("fail", "softfail", "permerror", "temperror")]
        missing = [k.upper() for k, v in auth.items() if v == "none"]
        passed = [k.upper() for k, v in auth.items() if v == "pass"]
        if failed:
            reasons.append(("Sender failed authentication checks",
                            "The mail server reported " + ", ".join(failed) + " as failed. "
                            "This means the email may not have come from the address it shows."))
        elif missing:
            reasons.append(("Sender could not be fully verified",
                            "No " + ", ".join(missing) + " record was found for the sender's domain, "
                            "so its identity was not confirmed."))
        elif passed:
            reasons.append(("Sender passed authentication checks",
                            ", ".join(passed) + " passed. The email came from the domain it claims - "
                            "but that domain could still be a lookalike or a hacked account."))
    frm = domain_of(header_field(headers, "From"))
    reply = domain_of(header_field(headers, "Reply-To"))
    if frm and reply and frm != reply:
        reasons.append(("Replies go to a different address",
                        f"Sent from {frm} but replies would go to {reply}. "
                        "A common trick to hijack a conversation."))
    return reasons


def build_reasons(text, feats):
    """Map structural features to plain-language indicators (NCSC-style)."""
    reasons = []

    urg = found_words(text, features.URGENCY_WORDS)
    if urg:
        reasons.append(("Pressure to act quickly",
                        "Phrases like " + ", ".join(f"“{w}”" for w in urg) +
                        ". Genuine messages rarely need you to act within hours."))

    cred = found_words(text, features.CREDENTIAL_WORDS)
    if cred:
        reasons.append(("Asks you to sign in, verify or confirm something",
                        "Mentions " + ", ".join(f"“{w}”" for w in cred) +
                        ". Your school's IT team will not ask for your password by email."))

    money = found_words(text, features.MONEY_WORDS)
    if money:
        reasons.append(("Mentions money, payment or bank details",
                        "Mentions " + ", ".join(f"“{w}”" for w in money) +
                        ". Requests to change payment details are a common scam."))

    if feats["n_urls"] > 0:
        plural = "link" if feats["n_urls"] == 1 else "links"
        reasons.append((f"Contains {feats['n_urls']} {plural}",
                        "Hover over a link to see where it really goes before clicking. "
                        "If the address doesn't match the organisation, don't click."))

    if feats["has_ip_url"]:
        reasons.append(("A link points to a raw number address",
                        "Addresses like http://192.168… instead of a name are a strong warning sign."))

    if feats["caps_ratio"] > 0.3 and feats["n_words"] > 5:
        reasons.append(("Lots of capital letters",
                        "Shouting in capitals is often used to create alarm."))

    if feats["n_exclaim"] >= 3:
        reasons.append(("Several exclamation marks",
                        "Unusual for professional email from a real organisation."))

    return reasons


def risk_band(p):
    """Turn a probability into a verdict, a colour and a sentence."""
    if p >= 0.70:
        return ("Likely phishing", "#B3261E",
                "Treat this email as unsafe. Do not click links or open attachments.")
    if p >= 0.35:
        return ("Be cautious", "#B26A00",
                "Some warning signs are present. Check with the sender through a different route before acting.")
    return ("Probably legitimate", "#1B6E3A",
            "Few warning signs found. Stay alert if it asks you to do anything unusual.")


# Page

st.set_page_config(page_title="Show Your Workfin", page_icon="🐟", layout="centered")

st.markdown(
    """
    <style>
      .block-container { max-width: 720px; padding-top: 2.5rem; }
      h1 { font-weight: 600; letter-spacing: -0.01em; margin-bottom: 0; }
      .tagline { font-size: 1.25rem; font-weight: 500; margin: 0.1rem 0 0.4rem 0; color: #1F5FA8; }
      .lead { color: #4a5568; margin-bottom: 1.5rem; }
      .verdict { border-left: 6px solid var(--c); padding: 0.9rem 1.1rem; margin: 1.2rem 0 0.4rem 0;
                 background: #ffffff; border-radius: 0 6px 6px 0; box-shadow: 0 1px 3px rgba(20,33,61,0.08); }
      .verdict .label { color: var(--c); font-weight: 600; font-size: 1.15rem; }
      .verdict .pct { font-size: 2.4rem; font-weight: 600; line-height: 1.1; margin: 0.15rem 0; color: #1a1a1a; }
      .verdict .advice { color: #333; }
      .reason { padding: 0.6rem 0.6rem; border-bottom: 1px solid #d6e2f0; background: #ffffff; }
      .reason:last-child { border-bottom: none; }
      .reason b { display: block; margin-bottom: 0.15rem; color: #1a1a1a; }
      .reason span { color: #4a4a4a; }
      .quiet { color: #6a6a6a; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🐟 Show Your Workfin")
st.markdown('<p class="tagline">Is this email safe?</p>', unsafe_allow_html=True)
st.markdown('<p class="lead">Paste the text of an email you\'re unsure about. '
            'You\'ll get an estimated phishing risk and the reasons behind it. '
            'Nothing you paste is stored.</p>', unsafe_allow_html=True)

email_text = st.text_area("Email text", height=220, label_visibility="collapsed",
                          placeholder="Paste the email here, including the subject line if you have it. We'll show our working.")

with st.expander("Optional: include the sender checks"):
    st.markdown(
        "If you paste the **full message source** instead of just the text, the checker can also "
        "report whether the sender passed the mail server's authentication checks (SPF, DKIM, DMARC).\n\n"
        "**What are those?** When an email arrives, your school's mail server runs three checks and "
        "writes the results into the hidden headers of the message:\n"
        "- **SPF** – was it sent from a server the sender's domain allows?\n"
        "- **DKIM** – does it carry a valid digital signature from that domain?\n"
        "- **DMARC** – does the sender's domain say what to do when those checks fail?\n\n"
        "A **fail** means the email probably didn't come from the address it shows. A **pass** means it "
        "did come from that domain – but a lookalike domain or a hacked account will pass too, so a pass "
        "isn't proof it's safe. That's why the wording check still runs either way.\n\n"
        "- **Outlook on the web:** open the email, click the three dots (⋯) → **View** → **View message source**, "
        "select all, copy, and paste here.\n"
        "- **Outlook desktop:** open the email, **File** → **Properties**, copy the text in *Internet headers*, "
        "then paste the email text below it with a blank line in between.\n\n"
        "This is optional. The checker works from the email text alone."
    )

check = st.button("Check this email", type="primary", use_container_width=True)

if check:
    if len(email_text.strip()) < 20:
        st.warning("Paste a bit more of the email. A few words aren't enough to judge.")
    else:
        model = load_model()
        headers, body = split_headers(email_text)      # headers is '' unless full source was pasted
        frame = features.make_frame([body])
        p = float(model.predict_proba(frame)[0, 1])
        feats = features.structural_features(body)
        label, colour, advice = risk_band(p)

        st.markdown(
            f'<div class="verdict" style="--c:{colour}">'
            f'<div class="label">{label}</div>'
            f'<div class="pct">{p*100:.0f}%</div>'
            f'<div class="quiet">estimated chance this is a phishing email</div>'
            f'<div class="advice" style="margin-top:0.6rem">{advice}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        reasons = header_reasons(headers) + build_reasons(body, feats)
        words = word_contributions(model, frame)

        st.subheader("Our working")
        if not reasons and not words:
            st.markdown('<p class="quiet">No specific warning signs stood out. '
                        'The score is based on the overall wording of the message.</p>',
                        unsafe_allow_html=True)
        for title, detail in reasons:
            st.markdown(f'<div class="reason"><b>{title}</b><span>{detail}</span></div>',
                        unsafe_allow_html=True)
        if words:
            wl = ", ".join(f"“{w}”" for w, _ in words)
            st.markdown(f'<div class="reason"><b>Wording that resembles known phishing emails</b>'
                        f'<span>{wl}</span></div>', unsafe_allow_html=True)

        st.subheader("What to do")
        st.markdown(
            "- Don't click links or open attachments you weren't expecting.\n"
            "- If it asks you to do something, check with the sender by phone or in person, "
            "not by replying.\n"
            "- Report it using your school's usual process, even if you're not sure."
        )

        st.markdown('<p class="quiet" style="margin-top:1.5rem">This tool is decision support, '
                    'not a guarantee. It looks at the wording of the message (and the sender checks if you pasted them), '
                    'not at links or attachments, and it can be wrong in both directions.</p>',
                    unsafe_allow_html=True)

with st.sidebar:
    st.markdown("**How it works**")
    st.markdown(
        "The checker was trained on around 90,000 real phishing and legitimate emails. "
        "It scores the wording of the message and lists the warning signs it found, "
        "based on National Cyber Security Centre guidance."
    )
    st.markdown("**Privacy**")
    st.markdown("The email text is analysed in memory and discarded. Nothing is saved or sent anywhere.")
    st.markdown("**About**")
    st.markdown("Show Your Workfin was built as an MSc Data Science project at UWE Bristol, 2026. "
                "It is decision support for school staff, not a replacement for your school's email filtering or reporting process.")