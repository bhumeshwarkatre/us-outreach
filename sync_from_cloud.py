import sqlite3, os
from dotenv import load_dotenv
from supabase import create_client
from config.settings import DATABASE_PATH

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

print("🌐 Pulling from Supabase...")
leads = supabase.table("leads").select("*").execute().data

conn = sqlite3.connect(DATABASE_PATH)
cur = conn.cursor()
new = 0
for l in leads:
    l.pop("id", None)
    cur.execute("INSERT OR IGNORE INTO leads (creator_name,email,platform,niche,followers,country,profile_url,status,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (l.get("creator_name"), l.get("email"), l.get("platform"), l.get("niche"), l.get("followers"), l.get("country"), l.get("profile_url"), l.get("status"), l.get("created_at")))
    new += cur.rowcount
conn.commit(); conn.close()
print(f"✅ Synced {new} new leads to local SQLite.")