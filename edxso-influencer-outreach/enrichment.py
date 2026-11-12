import re
import requests
from bs4 import BeautifulSoup

EMAIL_RE = re.compile(r"(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}")

def validate_email(value):
    value = str(value or "").strip()
    if not value or value.lower() in {"not found", "none", "nan", "n/a"}:
        return "Not Found"
    return value if EMAIL_RE.fullmatch(value) else "Not Found"

def enrich_public_website(url):
    """
    Optional, conservative extraction from a creator-provided public website.
    Only reads publicly visible page text; respects timeout and does not bypass logins.
    """
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        return []
    try:
        response = requests.get(url, timeout=8, headers={"User-Agent": "EDXSO-Assignment-Prototype/1.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text[:1_000_000], "html.parser")
        text = soup.get_text(" ", strip=True)
        return sorted(set(EMAIL_RE.findall(text)))
    except requests.RequestException:
        return []
