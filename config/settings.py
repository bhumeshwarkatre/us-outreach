import os

from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent.parent
)

load_dotenv(
    BASE_DIR / ".env"
)


DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "leads.db"
)


# =========================
# FOLLOWER FILTERS
# =========================

MIN_FOLLOWERS = 15000

MAX_FOLLOWERS = 100000


# =========================
# SEARCH SETTINGS
# =========================

MAX_QUERIES_PER_RUN = 25

MAX_RESULTS_PER_QUERY = 20

REQUEST_TIMEOUT = 15


# =========================
# HEADERS
# =========================

HEADERS = {

    "User-Agent": (

        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "

        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "

        "Chrome/137.0 Safari/537.36"
    )
}


# =========================
# EMAIL SETTINGS
# =========================

EMAIL_ADDRESS = os.getenv(
    "EMAIL_ADDRESS"
)

EMAIL_PASSWORD = os.getenv(
    "EMAIL_PASSWORD"
)

SMTP_SERVER = os.getenv(
    "SMTP_SERVER"
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        587
    )
)

IMAP_SERVER = os.getenv(
    "IMAP_SERVER"
)


# =========================
# SEARCH ENGINE
# =========================

SEARCH_ENGINE = (
    "https://www.google.com/search?q="
)