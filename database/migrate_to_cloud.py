import sys
import os
import sqlite3
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DATABASE_PATH
from supabase import create_client, Client

load_dotenv()

def migrate():
    # 1. Check Credentials
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")
        return

    # 2. Connect to Supabase
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return

    # 3. Connect to Local SQLite
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 4. Fetch Data
    print(" Reading local SQLite...")
    cursor.execute("SELECT * FROM leads")
    leads = cursor.fetchall()
    
    if not leads:
        print("ℹ No leads found in local SQLite.")
        conn.close()
        return

    print(f" Found {len(leads)} leads. Pushing to Supabase...")
    
    count = 0
    
    # 5. Upload Loop
    for lead in leads:
        data = dict(lead)
        
        
        if "id" in data:
            del data["id"]
            
        try:
            # Upsert prevents duplicates if you run this script multiple times
            supabase.table("leads").upsert(data, on_conflict="email").execute()
            count += 1
        except Exception as e:
            print(f"⚠️ Error syncing {data.get('email')}: {e}")
            
    conn.close()
    print(f" Migration Finished: {count} leads synced.")

if __name__ == "__main__":
    migrate()