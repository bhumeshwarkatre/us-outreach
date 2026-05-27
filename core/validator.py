import re
from typing import Optional

class Validator:

    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+'
        r'@[a-zA-Z0-9.-]+'
        r'\.[a-zA-Z]{2,}$'
    )

    URL_PATTERN = re.compile(
        r'^(https?:\/\/)?'
        r'([a-zA-Z0-9.-]+)\.'
        r'([a-zA-Z]{2,})'
        r'(\/.*)?$'
    )

    BLOCKED_EMAIL_PATTERNS = [
        "noreply@",
        "no-reply@",
        "mailer-daemon@",
        "postmaster@",
        "example.com",
        "domain.com",
        "@email.com",
        "accounts.google.com"
    ]

    INVALID_ENDINGS = (
        ".png", ".jpg", ".jpeg", ".webp",
        ".mp4", ".mov",
        ".html", ".htm",
        ".pdf", ".txt"
        # ✅ REMOVED ".read" — we now CLEAN it instead of rejecting
    )

    # ✅ Block .read anywhere in the domain, not just at the end
    BLOCKED_DOMAIN_PATTERN = re.compile(r'\.read(\.|$)', re.IGNORECASE)

    @staticmethod
    def clean_email(email: Optional[str]) -> Optional[str]:
        """
        Clean email: remove .read suffixes, whitespace, normalize case.
        Returns cleaned email or None if invalid after cleaning.
        """
        if not email or not isinstance(email, str):
            return None

        # 1. Strip whitespace & lowercase
        email = email.strip().lower()

        # 2. Remove tracking suffixes (Gmail read markers, etc.)
        email = re.sub(r'\.read$', '', email)       # user@domain.com.read
        email = re.sub(r'read$', '', email)         # user@domain.comread  
        email = re.sub(r'\?read=true$', '', email)  # user@domain.com?read=true
        email = re.sub(r'\?read=false$', '', email) # user@domain.com?read=false

        # 3. Strip common punctuation artifacts
        email = email.strip(" .,:;|<>[](){}")

        # 4. Return cleaned email (validation happens separately)
        return email if email else None

    @staticmethod
    def valid_email(email) -> bool:
        """
        Validates email (automatically cleans before checking).
        100% backward compatible: still returns True/False.
        """
        if not email:
            return False

        # ✅ CLEAN FIRST, then validate
        cleaned = Validator.clean_email(email)
        if not cleaned:
            return False

        # =====================
        # REGEX CHECK (on cleaned email)
        # =====================
        if not Validator.EMAIL_PATTERN.match(cleaned):
            return False

        # =====================
        # BLOCKED DOMAIN PATTERN
        # =====================
        domain = cleaned.split("@")[-1]
        if Validator.BLOCKED_DOMAIN_PATTERN.search(domain):
            return False

        # =====================
        # BLOCKED EMAILS
        # =====================
        for pattern in Validator.BLOCKED_EMAIL_PATTERNS:
            if pattern in cleaned:
                return False

        # =====================
        # INVALID ENDINGS (on cleaned email)
        # =====================
        for ending in Validator.INVALID_ENDINGS:
            if cleaned.endswith(ending):
                return False

        # =====================
        # DOUBLE DOTS
        # =====================
        if ".." in cleaned:
            return False

        return True

    @staticmethod
    def valid_url(url):
        if not url:
            return False
        url = url.strip()
        return bool(Validator.URL_PATTERN.match(url))

    @staticmethod
    def valid_text(text):
        if not text:
            return False
        text = text.strip()
        return len(text) > 3