# EDXSO AI Engineer Intern – Assignment 1
## AI Micro-Influencer Outreach System (Technology niche)

A functional prototype demonstrating the pipeline: discovery/import → filtering → enrichment → AI personalization → review → email sending/simulation → tracking.

## Technology stack
- Python 3.10+
- Streamlit dashboard
- Pandas for data processing
- YouTube Data API v3 (optional official discovery source)
- Gemini API (`google-genai`) for personalized message generation
- SQLite for outreach records and duplicate prevention
- SMTP for optional email delivery
- Requests + BeautifulSoup for optional public creator-website email lookup

## Important data integrity notes
- Do not submit invented influencer names, follower counts, engagement rates, or emails.
- YouTube Data API discovery returns public channel names, URLs and subscriber counts where visible. It does **not** provide engagement rate or contact email. These fields remain unavailable until independently verified.
- The YouTube subscriber count is not necessarily identical to cross-platform followers.
- A creator's public website may list a contact email; review the source and verify it before outreach.
- A CSV import is supported for records gathered from legitimate, documented sources.
- The app does not scrape private pages, bypass logins, or automate Instagram DMs.
- The 5,000–100,000 follower range and 2% engagement threshold are configurable example criteria. Adjust to the campaign brief.

## Setup (Windows PowerShell)
```powershell
cd path\to\edxso-influencer-outreach
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
streamlit run app.py
```

Add `GEMINI_API_KEY` to `.env` to enable AI personalization.
Add `YOUTUBE_API_KEY` to `.env` to use official YouTube channel discovery. Enable YouTube Data API v3 in Google Cloud Console and create an API key.
If the virtual environment activation is blocked in PowerShell, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Discovery methodology
1. Use the official YouTube Data API v3 search endpoint with `type=channel`.
2. Fetch channel details and subscriber counts with the channels endpoint.
3. Alternatively import a CSV with documented source URLs.
4. Keep source URL and checked timestamp for auditability.
5. Do not treat search results alone as proof of engagement rate, email, audience demographics, or a micro-influencer fit.

## Filtering logic
Default technology keywords: technology, tech, software, AI, gadgets, coding.
- Followers: 5,000–100,000 inclusive.
- Engagement: at least 2%.
- Niche/content: at least one configured keyword.
- Profile URL: must be an HTTP(S) URL.
A profile is marked Qualified only when all checks pass. Missing engagement data fails the threshold with a clear reason rather than being assumed.

## Enrichment
- Required fields are represented in the dataset template.
- Email validation marks missing or malformed values as `Not Found`.
- Optional website lookup extracts only email-like strings from a publicly accessible website URL supplied in the profile. It does not guess addresses. Manually verify any candidate.
- Audience demographics remain blank when unavailable.

## AI model and prompt
- Model default: `gemini-2.5-flash` (configurable with `GEMINI_MODEL`).
- Prompt uses the creator's supplied niche, content themes, platform and available metrics.
- It asks for a 60–90 word email and a 15–30 word DM.
- It explicitly prohibits inventing recent posts, personal details, audience demographics, brands, or relationships.
- Human review is required before sending.

## Sending mechanism
- Default is simulation: it records a simulated send without transmitting an email.
- Optional SMTP can be configured with sender credentials in `.env`.
- Live sending requires valid email, manual review, and no previous sent record for the profile.
- Instagram DM is manual only; no unauthorized automation is attempted.
- SQLite stores generated messages, delivery mode, status, timestamp and errors.

## Limitations
- YouTube API key is required for live YouTube discovery; Gemini key alone does not enable creator discovery.
- YouTube API does not provide engagement rate, email or audience demographics.
- Search results may include channels outside the selected niche; the filter is a first-pass classifier, not a guarantee of brand suitability.
- Real contact email and engagement data must be independently sourced and verified.
- The prototype does not provide Instagram/TikTok API discovery.
- SMTP sending depends on provider settings and account permissions.
- No campaign response/conversion analytics are available unless replies are manually imported.

## Submission checklist
- [ ] Import/discover at least 50 genuine records with source URLs.
- [ ] Verify required metrics and contact emails; keep unknown values as `Not Found`.
- [ ] Run classification and export `edxso_influencers_classified.csv`.
- [ ] Generate and review personalized messages for qualified creators.
- [ ] Demonstrate simulated sending and duplicate prevention.
- [ ] Capture screenshots of discovery, filtering, AI messages and tracker.
- [ ] Add screenshots and any approved data source notes to the repository.
