import sys
import os
import sqlite3
from dotenv import load_dotenv
from supabase import create_client
from config.settings import DATABASE_PATH

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")
        sys.exit(1)
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def pull():
    print("🌐 Pulling leads from Supabase → Local SQLite...")
    supabase = get_supabase()
    cloud_leads = supabase.table("leads").select("*").execute().data

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    for lead in cloud_leads:
        # ✅ UPSERT: Insert new OR update existing based on email
        cursor.execute("""
            INSERT INTO leads 
            (creator_name, email, platform, niche, followers, country, profile_url, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                status = excluded.status,
                creator_name = excluded.creator_name,
                platform = excluded.platform,
                niche = excluded.niche,
                followers = excluded.followers,
                country = excluded.country,
                profile_url = excluded.profile_url
        """, (
            lead.get("creator_name"), lead.get("email"), lead.get("platform"),
            lead.get("niche"), lead.get("followers"), lead.get("country"),
            lead.get("profile_url"), lead.get("status"), lead.get("created_at")
        ))
        
    conn.commit()
    conn.close()
    print(f"✅ Synced {len(cloud_leads)} leads (new + status updates) to local SQLite.\n")

def push():
    print("☁️ Pushing leads from Local SQLite → Supabase...")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads")
    columns = [desc[0] for desc in cursor.description]
    local_leads = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()

    supabase = get_supabase()
    for lead in local_leads:
        lead.pop("id", None)  # Let Supabase handle IDs
        supabase.table("leads").upsert(lead, on_conflict="email").execute()

    print(f"✅ Pushed {len(local_leads)} leads to Supabase.\n")

def status():
    supabase = get_supabase()
    cloud_leads = supabase.table("leads").select("*").execute().data
    cloud_count = len(cloud_leads)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM leads")
    local_count = cursor.fetchone()[0]
    conn.close()

    print(f"📊 Cloud (Supabase): {cloud_count} leads")
    print(f"💻 Local (SQLite): {local_count} leads")
    if cloud_count == local_count:
        print("✅ Synced perfectly.\n")
    else:
        print(f"⚠️ Mismatch: {abs(cloud_count - local_count)} leads out of sync.\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python sync.py pull    # Cloud → Local")
        print("  python sync.py push    # Local → Cloud")
        print("  python sync.py status  # Check sync counts")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "pull":
        pull()
    elif cmd == "push":
        push()
    elif cmd == "status":
        status()
    else:
        print("❌ Unknown command. Use: pull, push, or status")