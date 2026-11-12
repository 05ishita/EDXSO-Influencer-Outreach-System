import pandas as pd

def classify(df, min_followers=5000, max_followers=100000, min_engagement=2.0, niche_keywords=None):
    if df.empty:
        return df
    out = df.copy()
    niche_keywords = [x.strip().lower() for x in (niche_keywords or []) if x.strip()]
    reasons, statuses = [], []
    for _, row in out.iterrows():
        failures = []
        try:
            followers = float(row.get("followers", 0) or 0)
        except (TypeError, ValueError):
            followers = 0
        if not min_followers <= followers <= max_followers:
            failures.append(f"Followers outside {min_followers:,}–{max_followers:,}")
        engagement = row.get("engagement_rate")
        try:
            if pd.isna(engagement) or str(engagement).strip() == "":
                failures.append("Engagement rate unavailable; cannot verify threshold")
            elif float(engagement) < min_engagement:
                failures.append(f"Engagement below {min_engagement}%")
        except (TypeError, ValueError):
            failures.append("Engagement rate invalid or unavailable")
        searchable = " ".join([
            str(row.get("niche", "")),
            str(row.get("content_themes", "")),
            str(row.get("name", "")),
        ]).lower()
        if niche_keywords and not any(k in searchable for k in niche_keywords):
            failures.append("Niche/content does not match selected keywords")
        if not str(row.get("profile_url", "")).startswith(("http://", "https://")):
            failures.append("Profile URL missing or invalid")
        statuses.append("Qualified" if not failures else "Not Qualified")
        reasons.append("Passed all configured checks" if not failures else "; ".join(failures))
    out["status"] = statuses
    out["filter_reason"] = reasons
    return out
