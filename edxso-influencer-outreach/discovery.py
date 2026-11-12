import requests
from datetime import datetime, timezone

YOUTUBE_SEARCH = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_CHANNELS = "https://www.googleapis.com/youtube/v3/channels"

def discover_youtube(query, api_key, max_results=50):
    """
    Uses the official YouTube Data API v3. Requires the user's own API key.
    Searches public channels; subscriber counts may be hidden by channel owners.
    """
    if not api_key:
        raise ValueError("YouTube API key is not configured. Add YOUTUBE_API_KEY to .env, or import a sourced CSV.")
    collected = []
    page_token = None
    while len(collected) < max_results:
        params = {
            "part": "snippet",
            "type": "channel",
            "q": query,
            "maxResults": min(50, max_results - len(collected)),
            "key": api_key,
        }
        if page_token:
            params["pageToken"] = page_token
        response = requests.get(YOUTUBE_SEARCH, params=params, timeout=25)
        response.raise_for_status()
        payload = response.json()
        ids = [item["id"]["channelId"] for item in payload.get("items", [])]
        if ids:
            detail = requests.get(YOUTUBE_CHANNELS, params={
                "part": "snippet,statistics,brandingSettings",
                "id": ",".join(ids),
                "key": api_key,
            }, timeout=25)
            detail.raise_for_status()
            for item in detail.json().get("items", []):
                stats = item.get("statistics", {})
                snippet = item.get("snippet", {})
                followers = int(stats.get("subscriberCount", 0) or 0)
                collected.append({
                    "name": snippet.get("title", ""),
                    "platform": "YouTube",
                    "profile_url": f"https://www.youtube.com/channel/{item['id']}",
                    "followers": followers,
                    "engagement_rate": None,
                    "niche": query,
                    "content_themes": snippet.get("description", "")[:500],
                    "email": "Not Found",
                    "website": "",
                    "audience_age": "",
                    "audience_gender": "",
                    "audience_geography": "",
                    "source_url": f"https://www.youtube.com/channel/{item['id']}",
                    "source_checked_at": datetime.now(timezone.utc).isoformat(),
                    "data_note": "Subscriber count from YouTube Data API; engagement rate and contact email not provided by this endpoint."
                })
        page_token = payload.get("nextPageToken")
        if not page_token or not ids:
            break
    return collected[:max_results]
