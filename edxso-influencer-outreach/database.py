import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).parent / "outreach.db"

def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS outreach (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            influencer_key TEXT NOT NULL UNIQUE,
            influencer_name TEXT,
            email TEXT,
            email_message TEXT,
            dm_message TEXT,
            sent INTEGER DEFAULT 0,
            sent_at TEXT,
            status TEXT DEFAULT 'Not sent',
            delivery_mode TEXT DEFAULT 'Simulation',
            error TEXT
        )
        """)
        con.execute("""
        CREATE TABLE IF NOT EXISTS influencers (
            profile_url TEXT PRIMARY KEY,
            data_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
        con.commit()

def save_influencers(records):
    saved = 0
    with connect() as con:
        for record in records:
            item = dict(record)
            profile_url = str(item.get("profile_url") or "").strip()
            if not profile_url:
                continue

            data_json = json.dumps(item, default=str)
            con.execute("""
                INSERT INTO influencers (profile_url, data_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(profile_url) DO UPDATE SET
                    data_json=excluded.data_json,
                    updated_at=excluded.updated_at
            """, (profile_url, data_json, datetime.now(timezone.utc).isoformat()))
            saved += 1
        con.commit()
    return saved

def load_influencers():
    with connect() as con:
        rows = con.execute(
            "SELECT data_json FROM influencers ORDER BY updated_at DESC"
        ).fetchall()
    return [json.loads(row["data_json"]) for row in rows]

def influencer_key(profile_url, email):
    value = (profile_url or email or "").strip().lower().rstrip("/")
    return value

def save_generated(name, email, profile_url, email_message, dm_message):
    key = influencer_key(profile_url, email)
    if not key:
        return False, "Missing profile URL and email; cannot create a safe deduplication key."
    with connect() as con:
        row = con.execute("SELECT id FROM outreach WHERE influencer_key=?", (key,)).fetchone()
        if row:
            con.execute("""
                UPDATE outreach SET influencer_name=?, email=?, email_message=?, dm_message=?
                WHERE influencer_key=?
            """, (name, email, email_message, dm_message, key))
            con.commit()
            return True, "Updated existing outreach record."
        con.execute("""
            INSERT INTO outreach (influencer_key, influencer_name, email, email_message, dm_message)
            VALUES (?, ?, ?, ?, ?)
        """, (key, name, email, email_message, dm_message))
        con.commit()
    return True, "Saved."

def mark_sent(profile_url, email, mode="Simulation", error=None):
    key = influencer_key(profile_url, email)
    with connect() as con:
        if error:
            con.execute("""
                UPDATE outreach SET status='Failed', error=?, delivery_mode=? WHERE influencer_key=?
            """, (error, mode, key))
        else:
            con.execute("""
                UPDATE outreach SET sent=1, sent_at=?, status=?, delivery_mode=?, error=NULL
                WHERE influencer_key=?
            """, (datetime.now(timezone.utc).isoformat(), "Simulated" if mode == "Simulation" else "Sent", mode, key))
        con.commit()

def already_sent(profile_url, email):
    key = influencer_key(profile_url, email)
    with connect() as con:
        row = con.execute("SELECT sent, status FROM outreach WHERE influencer_key=?", (key,)).fetchone()
    return bool(row and row["sent"])

def get_logs():
    with connect() as con:
        rows = con.execute("SELECT * FROM outreach ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]
