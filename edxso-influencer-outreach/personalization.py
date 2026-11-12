import os
from google import genai

def generate_messages(profile, api_key=None, model=None):
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing. Add it to your .env file.")
    client = genai.Client(api_key=api_key)
    safe_profile = {
        "name": str(profile.get("name", "Creator"))[:100],
        "platform": str(profile.get("platform", ""))[:40],
        "niche": str(profile.get("niche", ""))[:120],
        "content_themes": str(profile.get("content_themes", ""))[:800],
        "followers": str(profile.get("followers", "")),
        "engagement_rate": str(profile.get("engagement_rate", "")),
    }
    prompt = f"""
You write respectful, transparent creator-collaboration outreach.
Use ONLY the supplied profile signals. Do not invent a recent post, personal detail,
audience demographic, brand, product, payment amount, or prior relationship.
If recent content is not supplied, refer generally to the creator's stated themes.
Return exactly these two sections:
EMAIL:
A subject line and a 60–90 word email body.
DM:
A 15–30 word Instagram DM.
Keep both natural, specific to the available niche/content themes, and avoid false claims.
Creator profile: {safe_profile}
"""
    response = client.models.generate_content(model=model, contents=prompt)
    text = (response.text or "").strip()
    if "EMAIL:" not in text or "DM:" not in text:
        raise ValueError("The AI response did not contain both EMAIL: and DM: sections. Please retry.")
    email_part = text.split("EMAIL:", 1)[1].split("DM:", 1)[0].strip()
    dm_part = text.split("DM:", 1)[1].strip()
    return email_part, dm_part, text
