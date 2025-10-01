import re
EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+")
PHONE_RE = re.compile(r"\+?\d[\d\s\-]{6,}\d")

def redact(text: str):
    text = EMAIL_RE.sub('[REDACTED_EMAIL]', text)
    text = PHONE_RE.sub('[REDACTED_PHONE]', text)
    return text
