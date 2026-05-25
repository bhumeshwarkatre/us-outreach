# import sqlite3

# from config.settings import DATABASE_PATH


# class Database:

#     def __init__(self):
#         self.conn = sqlite3.connect(DATABASE_PATH)
#         self.cursor = self.conn.cursor()

#     def create_tables(self):
#         with open("database/schema.sql", "r") as file:
#             self.cursor.executescript(file.read())
#             self.conn.commit()

#     def lead_exists(self, email, profile_url):

#         query = """
#         SELECT id
#         FROM leads
#         WHERE email = ?
#         OR profile_url = ?
#         """

#         self.cursor.execute(query, (email, profile_url))

#         return self.cursor.fetchone() is not None

#     def insert_lead(self, data):

#         query = """
#         INSERT INTO leads (
#             creator_name,
#             email,
#             platform,
#             niche,
#             followers,
#             country,
#             profile_url
#         )
#         VALUES (?, ?, ?, ?, ?, ?, ?)
#         """

#         self.cursor.execute(
#             query,
#             (
#                 data["creator_name"],
#                 data["email"],
#                 data["platform"],
#                 data["niche"],
#                 data["followers"],
#                 data["country"],
#                 data["profile_url"]
#             )
#         )

#         self.conn.commit()


import sqlite3
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from config.settings import DATABASE_PATH

# Load environment variables
load_dotenv()

# =========================
# SUPABASE INITIALIZATION
# =========================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client only if credentials exist
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"⚠️ Supabase client init warning: {e}")


class Database:
    """
    Hybrid Database Handler:
    - Primary: SQLite (local, fast, offline-ready)
    - Secondary: Supabase (cloud backup, async sync)
    """

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """Initialize local SQLite tables from schema.sql"""
        with open("database/schema.sql", "r") as file:
            self.cursor.executescript(file.read())
            self.conn.commit()

    def lead_exists(self, email, profile_url):
        """
        Check if lead already exists in SQLite.
        (Supabase sync is backup-only, so we check local first for speed)
        """
        query = """
        SELECT id
        FROM leads
        WHERE email = ?
        OR profile_url = ?
        """
        self.cursor.execute(query, (email, profile_url))
        return self.cursor.fetchone() is not None

    def _sync_to_supabase(self, data):
        """
        Internal: Attempt to sync lead to Supabase.
        Fail-safe: errors are logged but don't crash the app.
        """
        if not supabase:
            return  # Supabase not configured
        
        try:
            # Use upsert with conflict on email to avoid duplicates
            # This matches your UNIQUE constraint on email
            supabase.table("leads").upsert(
                data, 
                on_conflict="email"
            ).execute()
        except Exception as e:
            # Log warning but continue - local DB is the source of truth
            print(f"⚠️ Supabase sync warning (non-critical): {e}")

    def insert_lead(self, data):
        """
        HYBRID WRITE STRATEGY:
        1. Insert to SQLite (primary) - instant, reliable
        2. Attempt sync to Supabase (backup) - async, fail-safe
        
        Method signature unchanged → app.py requires ZERO modifications
        """
        # =========================
        # STEP 1: WRITE TO SQLITE (PRIMARY)
        # =========================
        query = """
        INSERT INTO leads (
            creator_name,
            email,
            platform,
            niche,
            followers,
            country,
            profile_url
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        self.cursor.execute(
            query,
            (
                data["creator_name"],
                data["email"],
                data["platform"],
                data["niche"],
                data["followers"],
                data["country"],
                data["profile_url"]
            )
        )
        self.conn.commit()  # Commit SQLite transaction

        # =========================
        # STEP 2: SYNC TO SUPABASE (BACKUP)
        # =========================
        self._sync_to_supabase(data)

    def get_all_leads(self):
        """
        Fetch all leads from SQLite for UI rendering.
        Returns list of dicts for easy pandas/streamlit integration.
        (Supabase is backup-only; reads stay local for speed)
        """
        self.cursor.execute("SELECT * FROM leads ORDER BY created_at DESC")
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def close(self):
        """Properly close SQLite connection"""
        if self.conn:
            self.conn.close()