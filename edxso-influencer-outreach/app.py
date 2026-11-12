import os
from pathlib import Path
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from database import init_db, save_generated, get_logs, already_sent, mark_sent, save_influencers, load_influencers
from discovery import discover_youtube
from filtering import classify
from enrichment import validate_email, enrich_public_website
from personalization import generate_messages
from outreach import send_email, split_subject_body

load_dotenv()
init_db()
st.set_page_config(page_title="EDXSO | AI Influencer Outreach", layout="wide")

REQUIRED = ["name", "platform", "profile_url", "followers", "engagement_rate", "niche", "content_themes", "email"]
OPTIONAL = ["website", "audience_age", "audience_gender", "audience_geography", "source_url", "source_checked_at"]

def normalize(df):
    df = df.copy()
    for col in REQUIRED + OPTIONAL:
        if col not in df.columns:
            df[col] = "" if col != "email" else "Not Found"
    df["followers"] = pd.to_numeric(df["followers"], errors="coerce")
    df["engagement_rate"] = pd.to_numeric(df["engagement_rate"], errors="coerce")
    df["email"] = df["email"].apply(validate_email)
    df["name"] = df["name"].fillna("").astype(str)
    df["profile_url"] = df["profile_url"].fillna("").astype(str)
    return df

def persist_df():
    if not st.session_state.df.empty:
        save_influencers(st.session_state.df.to_dict("records"))

if "df" not in st.session_state:
    stored_records = load_influencers()
    st.session_state.df = normalize(pd.DataFrame(stored_records)) if stored_records else pd.DataFrame(columns=REQUIRED + OPTIONAL)
if "messages" not in st.session_state:
    st.session_state.messages = {}

st.title("EDXSO | AI Micro-Influencer Outreach")
st.caption("Technology niche | Discovery -> Filtering -> Enrichment -> AI Personalization -> Outreach Tracking")
st.info("Data integrity: this prototype never invents influencer records, contact emails, follower counts, or engagement metrics. Missing values remain marked as unavailable.")

with st.sidebar:
    st.header("Configuration")
    st.write("Gemini API:", "[OK] Configured" if os.getenv("GEMINI_API_KEY") else "Missing")
    st.write("YouTube API:", "[OK] Configured" if os.getenv("YOUTUBE_API_KEY") else "Missing")
    st.caption("Add keys to .env and restart Streamlit.")
    st.divider()
    st.header("Filtering criteria")
    min_followers = st.number_input("Minimum followers", min_value=0, value=5000, step=1000)
    max_followers = st.number_input("Maximum followers", min_value=5000, value=100000, step=5000)
    min_engagement = st.number_input("Minimum engagement (%)", min_value=0.0, max_value=100.0, value=2.0, step=0.5)
    keywords = st.text_input("Niche keywords", value="technology, tech, software, AI, gadgets, coding")

tabs = st.tabs(["Overview", "Discover / Import", "Influencer Database", "AI Personalization", "Outreach Tracker"])

with tabs[0]:
    df = st.session_state.df
    qualified = int((df.get("status", pd.Series(dtype=str)) == "Qualified").sum()) if not df.empty else 0
    logs = get_logs()
    sent = sum(1 for x in logs if x["sent"])
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Discovered / Imported", len(df))
    c2.metric("Qualified", qualified)
    c3.metric("Emails sent / simulated", sent)
    c4.metric("Outreach records", len(logs))
    st.subheader("Workflow")
    st.markdown("**1. Discover/import** -> **2. Filter** -> **3. Enrich** -> **4. Generate messages** -> **5. Review/send** -> **6. Track**")
    st.warning("A 50+ record target is a data requirement, not a reason to fabricate data. Use official API discovery or import a sourced CSV with evidence URLs.")

with tabs[1]:
    st.subheader("A. Discover public YouTube channels")
    st.write("Uses the official YouTube Data API v3. It returns public channel details; this endpoint does not provide contact emails or engagement rates.")
    q = st.text_input("Search query", value="technology creator")
    count = st.number_input("Maximum channels to fetch", min_value=1, max_value=50, value=50)
    if st.button("Discover using YouTube API", type="primary"):
        try:
            records = discover_youtube(q, os.getenv("YOUTUBE_API_KEY"), int(count))
            if records:
                new_df = normalize(pd.DataFrame(records))
                st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True).drop_duplicates(subset=["profile_url"], keep="last")
                persist_df()
                st.success(f"Fetched {len(records)} public channel records. Missing engagement/email fields are intentionally not guessed.")
            else:
                st.warning("No channels returned for this query.")
        except Exception as e:
            st.error(str(e))
    st.divider()
    st.subheader("B. Import a sourced CSV")
    st.write("Required columns: " + ", ".join(REQUIRED))
    uploaded = st.file_uploader("Upload influencer CSV", type=["csv"])
    if uploaded is not None:
        try:
            imported = normalize(pd.read_csv(uploaded))
            st.caption(f"Rows in uploaded file: {len(imported)}")
            if st.button("Add imported records"):
                st.session_state.df = pd.concat([st.session_state.df, imported], ignore_index=True).drop_duplicates(subset=["profile_url"], keep="last")
                persist_df()
                st.success(f"Imported records. Current unique profiles: {len(st.session_state.df)}")
        except Exception as e:
            st.error(f"Could not read CSV: {e}")
    st.download_button("Download blank CSV template", data=Path("data/influencers_template.csv").read_bytes(), file_name="influencers_template.csv", mime="text/csv")

with tabs[2]:
    st.subheader("Filter and classify creators")
    df = st.session_state.df.copy()
    if not df.empty:
        if st.button("Run filtering now"):
            terms = [x.strip() for x in keywords.split(",")]
            df = classify(df, int(min_followers), int(max_followers), float(min_engagement), terms)
            st.session_state.df = df
            persist_df()
            st.success("Filtering completed.")
        if "status" not in df.columns:
            df = classify(df, int(min_followers), int(max_followers), float(min_engagement), [x.strip() for x in keywords.split(",")])
            st.session_state.df = df
            persist_df()
        show_cols = [c for c in ["name","platform","followers","engagement_rate","niche","email","status","filter_reason","profile_url"] if c in df.columns]
        st.markdown(df[show_cols].to_html(index=False, escape=True), unsafe_allow_html=True)
        st.download_button("Export classified dataset CSV", data=df.to_csv(index=False).encode("utf-8"), file_name="edxso_influencers_classified.csv", mime="text/csv")
        st.caption(f"{len(df)} records loaded. Qualified: {(df['status']=='Qualified').sum()}. Not qualified: {(df['status']=='Not Qualified').sum()}.")
    else:
        st.info("No influencer records yet. Discover channels or import a sourced CSV first.")
    st.divider()
    st.subheader("Optional public website email lookup")
    st.caption("Only use a creator-provided website URL. This does not scrape social platforms or bypass access controls.")
    if not df.empty:
        idx = st.selectbox("Choose profile", options=list(df.index), format_func=lambda i: f"{df.loc[i,'name']} Ã¢â‚¬â€ {df.loc[i,'profile_url']}")
        if st.button("Look for publicly listed email on website"):
            site = str(df.loc[idx, "website"] or "")
            found = enrich_public_website(site)
            if found:
                st.success("Publicly listed email candidate(s): " + ", ".join(found))
                st.warning("Review the source page and obtain permission/appropriate basis before outreach. Confirm the address manually before use.")
            else:
                st.info("No public email found on the supplied website. Keep as Not Found.")

with tabs[3]:
    st.subheader("Generate personalized email + Instagram DM")
    df = st.session_state.df

    if not df.empty:
        if "status" not in df.columns:
            df = classify(
                df,
                int(min_followers),
                int(max_followers),
                float(min_engagement),
                [x.strip() for x in keywords.split(",")]
            )
            st.session_state.df = df
            persist_df()

        st.info(
            "You can generate draft messages for discovered creators. "
            "Unverified creators remain unqualified; no contact details or metrics are invented."
        )

        idx = st.selectbox(
            "Select influencer",
            options=list(df.index),
            format_func=lambda i: (
                f"{df.loc[i, 'name']} ({df.loc[i, 'platform']}) - "
                f"{df.loc[i, 'status']}"
            )
        )

        profile = df.loc[idx].to_dict()

        # Convert missing pandas values into clear text before sending to Gemini.
        profile = {
            k: ("Unavailable" if pd.isna(v) else v)
            for k, v in profile.items()
        }

        st.json({
            k: profile.get(k)
            for k in [
                "name", "platform", "followers", "engagement_rate",
                "niche", "content_themes", "email", "status"
            ]
        })

        is_qualified = profile.get("status") == "Qualified"
        valid_email = validate_email(profile.get("email"))

        if not is_qualified:
            st.warning(
                "This creator is not qualified under the current criteria. "
                "Draft generation is for preview only."
            )

        if valid_email == "Not Found":
            st.caption(
                "No verified contact email is available. "
                "The email draft cannot be sent."
            )

        if st.button("Generate personalized drafts with Gemini", type="primary"):
            try:
                email_msg, dm_msg, raw = generate_messages(profile)

                st.session_state.messages[str(idx)] = {
                    "email": email_msg,
                    "dm": dm_msg
                }

                saved, save_message = save_generated(
                    str(profile.get("name", "Creator")),
                    str(profile.get("email", "Not Found")),
                    str(profile.get("profile_url", "")),
                    email_msg,
                    dm_msg
                )

                if saved:
                    st.success("Email and Instagram DM drafts generated and saved.")
                else:
                    st.warning(f"Drafts generated, but database save needs attention: {save_message}")

            except Exception as e:
                st.error(f"Generation failed: {e}")

        msg = st.session_state.messages.get(str(idx))

        if msg:
            st.markdown("**Email collaboration pitch**")
            st.text_area(
                "Email message",
                value=msg["email"],
                height=190,
                key=f"email_{idx}"
            )

            st.markdown("**Instagram DM (manual workflow)**")
            st.text_area(
                "Instagram DM",
                value=msg["dm"],
                height=120,
                key=f"dm_{idx}"
            )

            st.caption(
                "Review and edit drafts before use. No Instagram message is sent automatically."
            )
    else:
        st.info("Import or discover profiles first.")
with tabs[4]:
    st.subheader("Outreach sending and audit log")
    logs = get_logs()
    if logs:
        st.markdown(pd.DataFrame(logs).to_html(index=False, escape=True), unsafe_allow_html=True)
    else:
        st.info("Generated messages will appear here.")
    st.divider()
    st.write("Email sending is simulated by default. Configure SMTP in .env only if you are authorized to send from that mailbox. Review and approve each message before sending.")
    df = st.session_state.df
    if not df.empty:
        generated_rows = []
        for idx, msg in st.session_state.messages.items():
            try:
                row = df.loc[int(idx)].to_dict()
                generated_rows.append((int(idx), row, msg))
            except Exception:
                pass
        if generated_rows:
            options = [x[0] for x in generated_rows]
            selected = st.selectbox("Choose generated outreach", options=options, format_func=lambda i: f"{df.loc[i,'name']} Ã¢â‚¬â€ {df.loc[i,'email']}")
            row = df.loc[selected].to_dict()
            msg = st.session_state.messages[str(selected)]
            valid_email = validate_email(row.get("email"))
            st.write("Contact email:", valid_email)
            mode = st.radio("Delivery mode", ["Simulation (safe default)", "Live SMTP (requires configuration)"], horizontal=True)
            if st.button("Send / simulate email"):
                if valid_email == "Not Found":
                    st.error("Cannot send: no verified contact email. Email remains Not Found.")
                elif already_sent(row["profile_url"], valid_email):
                    st.error("Duplicate prevention: this profile has already been marked sent.")
                else:
                    subject, body = split_subject_body(msg["email"])
                    try:
                        if mode.startswith("Live"):
                            send_email(valid_email, subject, body)
                            mark_sent(row["profile_url"], valid_email, "SMTP")
                            st.success("Email sent through configured SMTP.")
                        else:
                            mark_sent(row["profile_url"], valid_email, "Simulation")
                            st.success("Simulated send recorded. No email was actually sent.")
                    except Exception as e:
                        mark_sent(row["profile_url"], valid_email, "SMTP", str(e))
                        st.error(f"Delivery failed: {e}")
            st.caption("Instagram DMs are displayed for manual sending only; no platform restrictions are bypassed.")

st.divider()
st.caption("EDXSO Assignment 1 prototype | Technology niche | Verify source data before outreach.")


