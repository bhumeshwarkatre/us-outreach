import re
import sqlite3
import pandas as pd
import streamlit as st

# from scheduler import start_scheduler
from database.db import Database

from config.settings import (
    DATABASE_PATH
)

from core.query_generator import (
    QueryGenerator
)

from core.search_collector import (
    SearchCollector
)

from core.country_detector import (
    CountryDetector
)

from core.niche_classifier import (
    NicheClassifier
)

from core.filters import (
    LeadFilters
)

from core.deduplicator import (
    Deduplicator
)

from core.validator import (
    Validator
)

from outreach.mailer import (
    Mailer
)

from outreach.sender import (
    OutreachSender
)

from outreach.inbox_checker import (
    InboxChecker
)

from outreach.auto_reply import (
    AutoReply
)


# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Creator Engine",
    layout="wide"
)


# =========================
# DATABASE
# =========================

db = Database()

db.create_tables()

#database
# =========================
# DATABASE (Cloud-Optimized)
# =========================

@st.cache_resource
def initialize_database():
    """
    Runs EXACTLY ONCE per cold start.
    Prevents repeated Supabase calls on every UI interaction.
    """
    db = Database()
    db.create_tables()
    
    # Cloud sync: Pulls Supabase → SQLite cache on startup only
    if supabase:
        try:
            response = supabase.table("leads").select("*").execute()
            cloud_leads = response.data
            
            if cloud_leads:
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                for lead in cloud_leads:
                    # INSERT OR IGNORE prevents duplicates on restart
                    cursor.execute("""
                        INSERT OR IGNORE INTO leads 
                        (creator_name, email, platform, niche, followers, country, profile_url, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        lead.get("creator_name"), lead.get("email"), lead.get("platform"),
                        lead.get("niche"), lead.get("followers"), lead.get("country"),
                        lead.get("profile_url"), lead.get("status"), lead.get("created_at")
                    ))
                conn.commit()
                conn.close()
                print(f"✅ Cloud cache restored: {len(cloud_leads)} leads")
        except Exception as e:
            print(f"⚠️ Cloud cache restore skipped: {e}")
            
    return db

# Initialize once (cached across reruns)
db = initialize_database()

# if "scheduler_started" not in st.session_state:
#     start_scheduler()
#     st.session_state["scheduler_started"] = True


# =========================
# FOLLOWER EXTRACTOR
# =========================

def extract_followers(text):
    """
    Extract real follower count from Google snippet.
    Handles all formats:
      "132,5K+ volgers"   -> 132500
      "211.1K+ followers" -> 211100
      "25K followers"     -> 25000
      "1.2M followers"    -> 1200000
      "592K+ followers"   -> 592000
      "25000 followers"   -> 25000
    Returns int or None.
    """

    if not text:
        return None

    text_lower = text.lower()

    patterns = [

        # e.g. "132,5K+ followers" or "211.1K+ volgers"
        r'([\d]+[.,][\d]+)\s*k\+?\s*'
        r'(?:followers?|volgers?|subs?|subscribers?)',

        # e.g. "25K+ followers"
        r'([\d]+)\s*k\+?\s*'
        r'(?:followers?|volgers?|subs?|subscribers?)',

        # e.g. "1.2M followers"
        r'([\d]+[.,][\d]+)\s*m\+?\s*'
        r'(?:followers?|volgers?|subs?|subscribers?)',

        # e.g. "2M followers"
        r'([\d]+)\s*m\+?\s*'
        r'(?:followers?|volgers?|subs?|subscribers?)',

        # e.g. "25000 followers"
        r'([\d,]+)\s*(?:followers?|volgers?|subs?)',

        # bare K+ format e.g. "592K+"
        r'([\d]+[.,][\d]+)k\+',
        r'([\d]+)k\+',
    ]

    for pattern in patterns:

        match = re.search(pattern, text_lower)

        if match:

            raw = match.group(1)

            # Normalize European decimal comma to dot
            # "132,5" -> "132.5"
            raw = raw.replace(',', '.')

            try:
                num = float(raw)
            except ValueError:
                continue

            full_match = match.group(0).lower()

            if 'm' in full_match:
                return int(num * 1_000_000)
            elif 'k' in full_match:
                return int(num * 1_000)
            else:
                return int(num)

    return None


# =========================
# CREATOR NAME EXTRACTOR
# =========================

def extract_creator_name(title):
    """
    Extract real creator name from Google title.
    Handles:
      "John Smith (@johnsmith) • Instagram..." -> "John Smith"
      "Shanna Salmon | Chicago Trainer (...)"  -> "Shanna Salmon"
      "KAYLA ITSINES (@kayla_itsines)"         -> "KAYLA ITSINES"
      "johnsmith • Instagram photos..."        -> "johnsmith"
    """

    if not title:
        return "Unknown"

    # Capture everything before (@handle), bullet, or pipe
    match = re.match(
        r'^([^(@|]+?)(?:\s*[@(|]|$)',
        title.strip()
    )

    if match:
        name = match.group(1).strip(" |-•")
        if name and len(name) > 1:
            return name

    # Fallback: first part before bullet
    part = title.split("•")[0].strip()
    if part:
        return part

    return "Unknown"


# =========================
# SYSTEM EMAIL FILTER
# =========================

IGNORED_SENDERS = [
    "no-reply@accounts.google.com",
    "noreply@",
    "no-reply@",
    "mailer-daemon@",
    "postmaster@",
    "security@",
    "accounts.google.com",
]


def is_system_email(sender):
    if not sender:
        return True
    sender_lower = sender.lower()
    return any(
        ignored in sender_lower
        for ignored in IGNORED_SENDERS
    )


# =========================
# SIDEBAR
# =========================

menu = st.sidebar.selectbox(

    "Navigation",

    [
        "Dashboard",
        "Run Scraper",
        "Leads",
        "Outreach",
        "Inbox"
    ]
)


# =========================
# DASHBOARD
# =========================

if menu == "Dashboard":

    st.title(
        "Creator Engine Dashboard"
    )

    conn = sqlite3.connect(
        DATABASE_PATH
    )

    try:

        leads_df = pd.read_sql_query(
            "SELECT * FROM leads",
            conn
        )

    finally:

        conn.close()

    total_leads = len(leads_df)

    sent_count = len(
        leads_df[leads_df["status"] == "sent"]
    )

    new_count = len(
        leads_df[leads_df["status"] == "new"]
    )

    usa_count = len(
        leads_df[leads_df["country"] == "USA"]
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Leads", total_leads)

    with col2:
        st.metric("New Leads", new_count)

    with col3:
        st.metric("Emails Sent", sent_count)

    with col4:
        st.metric("USA Leads", usa_count)

    st.divider()

    st.subheader("Recent Leads")

    st.dataframe(
        leads_df.tail(20),
        width='stretch'
    )


# =========================
# RUN SCRAPER
# =========================

elif menu == "Run Scraper":

    st.title(
        "Dynamic Creator Scraper"
    )

    run_count = st.slider(
        "Queries Per Run",
        1,
        50,
        10
    )

    start_button = st.button(
        "Start Scraping"
    )

    if start_button:

        query_generator = QueryGenerator()
        niche_classifier = NicheClassifier()
        deduplicator = Deduplicator(db)
        search_collector = None

        progress = st.progress(0)
        logs = st.empty()

        saved_count = 0
        total_results = 0
        total_emails = 0
        stopped_due_to_captcha = False

        try:

            # =====================
            # START BROWSER
            # =====================

            search_collector = SearchCollector()

            # =====================
            # MAIN LOOP
            # =====================

            for i in range(run_count):

                generated = (
                    query_generator.generate_query()
                )

                query = generated["query"]

                logs.info(
                    f"[QUERY] {query}"
                )

                # =====================
                # SEARCH
                # =====================

                results = search_collector.search(
                    query=query,
                    max_pages=1
                )

                # =====================
                # CAPTCHA CHECK
                # =====================

                if search_collector.is_captcha_page():

                    stopped_due_to_captcha = True

                    logs.warning(
                        "[STOPPED] CAPTCHA still active."
                    )

                    break

                total_results += len(results)

                # =====================
                # PROCESS RESULTS
                # =====================

                for result in results:

                    try:

                        title = result.get(
                            "title", ""
                        )

                        snippet = result.get(
                            "snippet", ""
                        )

                        url = result.get(
                            "url", ""
                        )

                        platform = result.get(
                            "platform", "instagram"
                        )

                        emails = result.get(
                            "emails", []
                        )

                        # =====================
                        # VALID URL
                        # =====================

                        if not Validator.valid_url(url):
                            continue

                        # =====================
                        # EMAIL EXISTS
                        # =====================

                        if not emails:
                            continue

                        # =====================
                        # CONTENT
                        # =====================

                        content = f"{title} {snippet}"

                        # =====================
                        # CREATOR NAME
                        # Real name from title
                        # =====================

                        creator_name = (
                            extract_creator_name(title)
                        )

                        # =====================
                        # COUNTRY DETECTION
                        # =====================

                        country = (
                            CountryDetector.detect(content)
                        )

                        if not country:
                            country = "USA"

                        # =====================
                        # NICHE DETECTION
                        # =====================

                        detected_niche = (
                            niche_classifier.classify(content)
                        )

                        if not detected_niche:
                            detected_niche = generated["niche"]

                        # =====================
                        # FOLLOWER EXTRACTION
                        # Real count from snippet
                        # =====================

                        followers = extract_followers(content)

                        if not followers:
                            followers = 25000

                        logs.info(
                            f"[PARSED] "
                            f"name={creator_name} | "
                            f"followers={followers} | "
                            f"niche={detected_niche} | "
                            f"country={country}"
                        )

                        # =====================
                        # FOLLOWER FILTER
                        # =====================

                        if not LeadFilters.valid_followers(
                            followers
                        ):
                            logs.warning(
                                f"[SKIP] Followers "
                                f"out of range: {followers}"
                            )
                            continue

                        # =====================
                        # PROCESS EMAILS
                        # =====================

                        for email in emails:

                            if not Validator.valid_email(
                                email
                            ):
                                continue

                            # =====================
                            # DUPLICATE CHECK
                            # =====================

                            if deduplicator.is_duplicate(
                                email, url
                            ):
                                continue

                            # =====================
                            # LEAD OBJECT
                            # All real extracted data
                            # =====================

                            lead = {

                                "creator_name":
                                    creator_name,

                                "email":
                                    email,

                                "platform":
                                    platform,

                                "niche":
                                    detected_niche,

                                "followers":
                                    followers,

                                "country":
                                    country,

                                "profile_url":
                                    url
                            }

                            # =====================
                            # SAVE LEAD
                            # =====================

                            db.insert_lead(lead)

                            saved_count += 1
                            total_emails += 1

                            logs.success(
                                f"[SAVED] {email} | "
                                f"name={creator_name} | "
                                f"followers={followers} | "
                                f"niche={detected_niche}"
                            )

                    except Exception as inner_error:

                        logs.error(
                            f"[PROCESS ERROR] "
                            f"{inner_error}"
                        )

                progress.progress(
                    (i + 1) / run_count
                )

        except Exception as error:

            logs.error(
                f"[SCRAPER ERROR] {error}"
            )

        finally:


            # =====================
            # AUTO CLOSE BROWSER
            # =====================

            if search_collector is not None:
                search_collector.close()

        # =====================
        # FINAL STATUS
        # =====================

        if stopped_due_to_captcha:

            st.warning(
                "Scraping stopped because "
                "CAPTCHA is still active."
            )

        else:

            st.success(
                f"Scraping Completed\n\n"
                f"Queries Run: {run_count}\n\n"
                f"Results Found: {total_results}\n\n"
                f"Emails Extracted: {total_emails}\n\n"
                f"Leads Saved: {saved_count}"
            )


# =========================
# LEADS
# =========================

elif menu == "Leads":

    st.title(
        "Lead Database"
    )

    conn = sqlite3.connect(
        DATABASE_PATH
    )

    try:

        leads_df = pd.read_sql_query(
            "SELECT * FROM leads",
            conn
        )

    finally:

        conn.close()

    st.dataframe(
        leads_df,
        use_container_width=True
    )

    csv = leads_df.to_csv(index=False)

    st.download_button(
        label="Export CSV",
        data=csv,
        file_name="leads.csv",
        mime="text/csv"
    )

# //new lead

with st.form("manual_lead_form"):

    name = st.text_input("Creator Name")
    email = st.text_input("Email")
    platform = st.text_input("Platform")
    niche = st.text_input("Niche")
    followers = st.number_input("Followers")
    country = st.text_input("Country")
    url = st.text_input("Profile URL")

    submit = st.form_submit_button("Add Lead")

# if submit:
#             db.cursor.execute("""
#                 INSERT INTO leads (
#                 creator_name, email, platform,
#                 niche, followers, country,
#                 profile_url, status
#             )
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#             """, (
#                 name, email, platform,
#                 niche, followers, country,
#                 url, "new"
#                 ))

#             db.conn.commit()
#             st.success("Lead added successfully")

if submit:
    db.insert_lead({
        "creator_name": name,
        "email": email,
        "platform": platform,
        "niche": niche,
        "followers": followers,
        "country": country,
        "profile_url": url
    })
    st.success("Lead added successfully")

# delete lead

emails_to_delete = st.text_area(
    "Enter emails (one per line)"
)

if st.button("Delete Multiple Leads"):

    email_list = [

        email.strip().lower()

        for email in emails_to_delete.splitlines()

        if email.strip()
    ]

    if email_list:

        placeholders = ",".join(
            ["?"] * len(email_list)
        )

        query = f"""
        DELETE FROM leads
        WHERE LOWER(email) IN ({placeholders})
        """

        db.cursor.execute(
            query,
            email_list
        )

        deleted_count = db.cursor.rowcount

        db.conn.commit()

        deleted_emails = "\n".join(email_list)

        st.success(
            f"✅ Successfully deleted "
            f"{deleted_count} lead(s)."
        )

        st.info(
            f"Deleted Emails:\n\n{deleted_emails}"
        )

        st.rerun()

    else:

        st.warning(
            "⚠️ No emails entered."
        )

# =========================
# OUTREACH
# =========================

elif menu == "Outreach":

    st.title(
        "Cold Email Outreach"
    )

    conn = sqlite3.connect(
        DATABASE_PATH
    )

    query = """
    SELECT *
    FROM leads
    WHERE status = 'new' OR status IS NULL
    LIMIT 20
    """

    try:

        leads_df = pd.read_sql_query(
            query,
            conn
        )

    finally:

        conn.close()

    st.subheader("Pending Leads")

    st.dataframe(
        leads_df,
        width='stretch'
    )

    if st.button("Send Outreach Emails"):

        mailer = Mailer()

        sender = OutreachSender(db, mailer)

        leads = leads_df.to_dict(orient="records")

        sent_count = sender.send_bulk(leads)

        st.success(f"{sent_count} emails sent.")


# =========================
# INBOX
# =========================

elif menu == "Inbox":

    st.title("Inbox Replies")

    if st.button("Check Inbox"):

        mailer = Mailer()

        inbox_checker = InboxChecker(db, mailer)

        auto_reply = AutoReply(db, mailer)

        replies = inbox_checker.check_replies()

        # Filter out system/noreply emails
        real_replies = [
            r for r in replies
            if not is_system_email(
                r.get("sender", "")
            )
        ]

        if not real_replies:

            st.info("No new creator replies found.")

        else:

            st.caption(
                f"{len(real_replies)} reply(s) found"
            )

            for index, reply in enumerate(real_replies):

                # Compact collapsible card
                label = (
                    f"{'✅' if reply['interested'] else '📧'} "
                    f"{reply.get('sender', 'Unknown')} — "
                    f"{reply.get('subject', 'No Subject')}"
                )

                with st.expander(
                    label,
                    expanded=reply["interested"]
                ):

                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(
                            f"**From:** "
                            f"{reply.get('sender', '—')}  \n"
                            f"**Subject:** "
                            f"{reply.get('subject', '—')}"
                        )

                    with col2:
                        if reply["interested"]:
                            st.success("Interested")
                        else:
                            st.warning("Not interested")

                    body = reply.get("body", "").strip()

                    # Cap at 500 chars to stay compact
                    preview = (
                        body[:500] + "..."
                        if len(body) > 500
                        else body
                    )

                    st.text(preview)

                    if reply["interested"]:

                        if st.button(
                            "Send Auto Reply",
                            key=f"reply_btn_{index}"
                        ):

                            auto_reply.send_reply(
                                recipient=reply["sender"],
                                creator_name="Creator"
                            )

                            st.success("Auto reply sent.")