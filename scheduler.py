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

    try:

        print(
            "[SCHEDULER] Starting "
            "scheduled outreach..."
        )

        # =====================
        # OWN CONNECTION
        # new thread = new connection
        # =====================

        conn = sqlite3.connect(DATABASE_PATH)

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        # =====================
        # FETCH NEW LEADS
        # =====================

        cursor.execute("""
            SELECT * FROM leads
            WHERE status = 'new'
            OR status IS NULL
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

        local_db = LocalDB(conn, cursor)

        # =====================
        # SEND EMAILS
        # =====================

        mailer = Mailer()

        sender = OutreachSender(local_db, mailer)

        sent = sender.send_bulk(valid_leads)

        print(
            f"[SCHEDULER] "
            f"Completed. {sent} emails sent."
        )

        conn.close()

    except Exception as e:

        print(
            f"[SCHEDULER ERROR] {e}"
        )


# =========================
# START SCHEDULER
# =========================

def start_scheduler():

    scheduler = BackgroundScheduler(
        timezone=IST
    )

    # =====================
    # 6:05 PM IST
    # =====================

    scheduler.add_job(

        func=send_scheduled_outreach,

        trigger=CronTrigger(
            hour=19,
            minute=00,
            timezone=IST
        ),

        id="outreach_7pm",

        name="Outreach 7PM IST",

        replace_existing=True
    )

    # =====================
    # 10:00 PM IST
    # =====================

    scheduler.add_job(

        func=send_scheduled_outreach,

        trigger=CronTrigger(
            hour=22,
            minute=0,
            timezone=IST
        ),

        id="outreach_10pm",

        name="Outreach 10PM IST",

        replace_existing=True
    )

    scheduler.start()

    print(
        "[SCHEDULER] Background scheduler started.\n"
        "[SCHEDULER] Jobs: 7:00 PM IST, 10:00 PM IST"
    )

    return scheduler