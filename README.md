# EDXSO AI Engineer Intern – Assignment 1
## AI-Powered Micro-Influencer Outreach System

An AI-assisted influencer discovery, qualification, profile enrichment, and personalized outreach prototype focused on the Technology niche.

**Developer:** Ishita Singh  
**GitHub:** [05ishita](https://github.com/05ishita)  
**Project:** Automated Micro-Influencer Outreach System

## 1. Project Overview

This project demonstrates an end-to-end workflow for discovering technology creators, collecting publicly available profile information, classifying influencers against campaign criteria, generating personalized outreach messages, and tracking outreach activity.

### Workflow

Discovery → Data Collection → Filtering → Enrichment → AI Personalization → Human Review → Sending/Simulation → Tracking

## 2. Technology Stack

- Python 3
- Streamlit
- Pandas
- YouTube Data API v3
- Google Gemini API (`google-genai`)
- SQLite
- SMTP (optional email delivery)
- Requests and BeautifulSoup (optional public website enrichment)

## 3. Project Features

- Discover public YouTube channels using the official YouTube Data API.
- Import influencer records through CSV.
- Store influencer profiles in SQLite.
- Filter creators by follower range, engagement rate, niche relevance, and profile URL.
- Mark incomplete or unqualified records with clear reasons.
- Validate contact email fields without guessing missing addresses.
- Generate personalized email and Instagram DM drafts using Gemini when API access is available.
- Review messages before outreach.
- Simulate email sending by default.
- Prevent duplicate outreach and maintain an outreach log.
- Keep Instagram DM outreach manual.

## 4. Dataset and Current Test Results

The current discovery test collected 50 public YouTube channel records in the Technology niche.

| Metric | Current result |
|---|---:|
| Discovered channel records | 50 |
| Records within 5,000–100,000 followers | 4 |
| Qualified records | 0 |
| Not Qualified records | 50 |
| Verified engagement rates | 0 |
| Verified contact emails | 0 |

**Important:** These are the actual results of the current test run, not fabricated or estimated figures.

The YouTube Data API provides public channel information and subscriber counts where available, but does not provide engagement rates or creator contact emails through the discovery endpoint used here.

Consequently, missing engagement data is not assumed to meet the campaign threshold. All 50 records currently remain Not Qualified under the configured criteria.

Dataset files:
- `edxso_influencers_classified.csv` – exported classified records.
- `data/influencers_template.csv` – CSV import template.

## 5. Filtering Criteria

Default example criteria:

- Followers: 5,000–100,000 inclusive.
- Engagement rate: at least 2%.
- Niche/content relevance: at least one configured technology keyword.
- Profile URL: valid HTTP or HTTPS URL.

A record is qualified only when all required checks pass. Missing metrics are treated as unavailable and are not fabricated.

## 6. AI Personalization

The application uses the creator's available profile information, niche, platform, and content themes to generate:

- Email collaboration pitches of 60–90 words.
- Instagram DM drafts of 15–30 words.

The prompt is designed to avoid inventing recent posts, audience demographics, personal details, or brand relationships.

AI-generated content must be reviewed before outreach. Availability depends on a valid Gemini API key, model access, quota, and service availability.

## 7. Outreach and Tracking

- Simulation is the default delivery mode.
- Optional SMTP delivery can be configured.
- Live sending requires a valid contact email, human review, and duplicate checks.
- Instagram DMs are manual; unauthorized automation is not used.
- SQLite stores generated messages and outreach status.

## 8. Installation and Setup

### Requirements

- Python 3.10 or later
- pip
- API keys for optional YouTube discovery and Gemini personalization

### Windows PowerShell

```powershell
git clone https://github.com/05ishita/EDXSO-Influencer-Outreach-System.git
cd EDXSO-Influencer-Outreach-System/edxso-influencer-outreach

py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file in the project directory and configure the required keys:

```env
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_available_gemini_model

SMTP_HOST=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=
```

Never commit `.env` or real API credentials to GitHub.

### Run the application

```powershell
streamlit run app.py
```

Open the local Streamlit URL displayed in the terminal.

## 9. Data Sources and Responsible Use

- YouTube Data API v3 for public channel discovery.
- Public creator websites may be checked for openly published contact details.
- CSV imports may be used for independently sourced and documented records.

The application does not bypass logins, access private profiles, guess email addresses, or automate unauthorized Instagram messages.

## 10. Current Limitations and Future Improvements

Current limitations:
- The current test contains 50 discovered records but zero qualified records.
- Engagement rates and contact emails have not yet been independently verified.
- YouTube discovery does not provide Instagram or TikTok profile discovery.
- Gemini generation depends on API availability and quota.
- SMTP delivery requires valid provider configuration.
- Campaign response and conversion analytics are not yet implemented.

Planned improvements:
- Add more verified influencer discovery sources.
- Independently verify engagement metrics and public contact information.
- Improve niche and brand-fit classification.
- Add more platform integrations where permitted.
- Add campaign response and conversion analytics.

## 11. Submission Contents

- Python application source code.
- Influencer discovery and filtering modules.
- Profile enrichment and personalization modules.
- SQLite database and outreach tracking logic.
- Influencer CSV template.
- Classified influencer dataset export.
- Project documentation.

---

**Assignment:** EDXSO AI Engineer Intern – Assignment 1  
**Project:** Automated Micro-Influencer Outreach System  
**Niche:** Technology
