import os
import time
import sqlite3
import pytz

from apscheduler.schedulers.background import (
    BackgroundScheduler
)

from apscheduler.triggers.cron import (
    CronTrigger
)

from outreach.mailer import Mailer
from outreach.sender import OutreachSender
from core.validator import Validator
from config.settings import DATABASE_PATH


# =========================
# TIMEZONE
# =========================

IST = pytz.timezone("Asia/Kolkata")


# =========================
# OUTREACH JOB
# =========================

def send_scheduled_outreach():
    print("🚨 CANARY v3.0: Supabase sync ACTIVE - Commit d3dd72d")

    try:

        print(
            "[SCHEDULER] Starting "
            "scheduled outreach..."
        )

        # ✅ CRITICAL: Initialize Supabase client INSIDE function (has access to env vars)
        try:
            from supabase import create_client
            _SUPABASE_URL = os.getenv("SUPABASE_URL")
            _SUPABASE_KEY = os.getenv("SUPABASE_KEY")
            if _SUPABASE_URL and _SUPABASE_KEY:
                supabase_client = create_client(_SUPABASE_URL, _SUPABASE_KEY)
                print("[CLOUD] ✅ Supabase client initialized")
            else:
                supabase_client = None
                print("[CLOUD] ⚠️ Missing SUPABASE_URL or SUPABASE_KEY")
        except Exception as e:
            supabase_client = None
            print(f"[CLOUD] 💥 Failed to init Supabase client: {e}")

        # =====================
        # LOCK FILE
        # Prevents multiple instances from running simultaneously
        # =====================
        lock_file = "scheduler.lock"
        if os.path.exists(lock_file):
            print("[SCHEDULER] Another instance is already running. Exiting.")
            return
        
        with open(lock_file, "w") as f:
            f.write(str(time.time()))

        try:

            # =====================
            # OWN CONNECTION
            # new thread = new connection
            # =====================

            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)

            conn.row_factory = sqlite3.Row

            cursor = conn.cursor()

            # =====================
            # FETCH NEW LEADS
            # =====================

            # ✅ ORDER BY ensures we always pick the oldest unsent leads first
            cursor.execute("""
                SELECT * FROM leads
                WHERE status = 'new'
                OR status IS NULL
                ORDER BY created_at ASC
                LIMIT 20
            """)

            rows = cursor.fetchall()

            if not rows:

                print(
                    "[SCHEDULER] "
                    "No new leads found."
                )

                conn.close()

                return

            # =====================
            # BUILD LEAD DICTS
            # =====================

            leads = [
                dict(row)
                for row in rows
            ]

            print(
                f"[SCHEDULER] "
                f"Total fetched: {len(leads)}"
            )

            # ✅ IMMEDIATELY LOCK ROWS TO PREVENT DUPLICATES
            for lead in leads:
                cursor.execute(
                    "UPDATE leads SET status = 'processing' WHERE id = ?",
                    (lead["id"],)
                )
            conn.commit()  # ✅ Locks them before sending starts

            # =====================
            # VALIDATE EMAILS
            # =====================

            valid_leads = [
                lead for lead in leads
                if Validator.valid_email(
                    lead.get("email", "")
                )
            ]

            if not valid_leads:

                print(
                    "[SCHEDULER] "
                    "No valid leads after filtering."
                )

                conn.close()

                return

            print(
                f"[SCHEDULER] "
                f"Valid leads to send: "
                f"{len(valid_leads)}"
            )

            # =====================
            # LOCAL DB WRAPPER
            # mimics db object so
            # OutreachSender works unchanged
            # =====================

            class LocalDB:

                def __init__(self, conn, cursor):
                    self.conn = conn
                    self.cursor = cursor
                
                # ✅ Updated: Updates SQLite only (cloud sync handled separately below)
                def update_lead_status(self, email, new_status):
                    try:
                        self.cursor.execute(
                            "UPDATE leads SET status = ? WHERE email = ?",
                            (new_status, email)
                        )
                        self.conn.commit()  # ✅ ATOMIC COMMIT
                        print(f"[DB] ✅ SQLite updated: {email} → {new_status}")
                    except Exception as e:
                        print(f"[LOCAL_DB ERROR] {e}")  

            local_db = LocalDB(conn, cursor)

            # =====================
            # SEND EMAILS
            # =====================

            mailer = Mailer()

            sender = OutreachSender(local_db, mailer)

            sent = sender.send_bulk(valid_leads)

            # ✅ CRITICAL: Direct Supabase sync for all sent leads (bypasses LocalDB wrapper)
            if supabase_client and sent > 0:
                print(f"[CLOUD] Syncing {sent} sent leads to Supabase...")
                for lead in valid_leads:
                    try:
                        # Check if this lead was actually sent (status should be 'sent' in SQLite)
                        cursor.execute("SELECT status FROM leads WHERE email = ?", (lead["email"],))
                        row = cursor.fetchone()
                        if row and row[0] == "sent":
                            supabase_client.table("leads").update(
                                {"status": "sent"}
                            ).eq("email", lead["email"]).execute()
                            print(f"[CLOUD] ✅ Supabase updated: {lead['email']} → sent")
                    except Exception as cloud_err:
                        print(f"[CLOUD] ⚠️ Failed to sync {lead['email']}: {cloud_err}")

            print(
                f"[SCHEDULER] "
                f"Completed. {sent} emails sent."
            )

            conn.close()

        finally:
            # ✅ Always remove lock file when job finishes
            if os.path.exists(lock_file):
                os.remove(lock_file)

    except Exception as e:

        print(
            f"[SCHEDULER ERROR] {e}"
        )
        # Clean up lock on unexpected crashes too
        if os.path.exists("scheduler.lock"):
            os.remove("scheduler.lock")


# =========================
# START SCHEDULER
# =========================

def start_scheduler():

    scheduler = BackgroundScheduler(
        timezone=IST
    )

    # =====================
    # 5:15 PM IST (Morning USA)
    # =====================

    scheduler.add_job(

        func=send_scheduled_outreach,

        trigger=CronTrigger(
            hour=17,
            minute=15,
            timezone=IST
        ),

        id="outreach_5:15_pm",

        name="Outreach 5:15 PM IST",

        replace_existing=True
    )

    # =====================
    # 5:30 AM IST (Evening USA)
    # =====================

    scheduler.add_job(

        func=send_scheduled_outreach,

        trigger=CronTrigger(
            hour=5,
            minute=30,
            timezone=IST
        ),

        id="outreach_5:30_am",

        name="Outreach 5:30 AM IST",

        replace_existing=True
    )

    scheduler.start()

    print(
        "[SCHEDULER] Background scheduler started.\n"
        "[SCHEDULER] Jobs: 5:15 PM IST & 5:30 AM IST"
    )

    return scheduler"# Refreshed $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" 
