import re


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
        ".pdf", ".txt",
        ".read"
    )

    # ✅ Block .read anywhere in the domain, not just at the end
    BLOCKED_DOMAIN_PATTERN = re.compile(r'\.read(\.|$)', re.IGNORECASE)

    @staticmethod
    def valid_email(email):
        if not email:
            return False

        email = email.lower().strip()

        # ✅ REMOVED: email.replace(".read", "") — this was the bug

        email = email.strip(" .,:;|<>[](){}")

        # =====================
        # REGEX CHECK
        # =====================
        if not Validator.EMAIL_PATTERN.match(email):
            return False

        # =====================
        # BLOCKED DOMAIN PATTERN  ✅ NEW
        # =====================
        domain = email.split("@")[-1]
        if Validator.BLOCKED_DOMAIN_PATTERN.search(domain):
            return False

        # =====================
        # BLOCKED EMAILS
        # =====================
        for pattern in Validator.BLOCKED_EMAIL_PATTERNS:
            if pattern in email:
                return False

        # =====================
        # INVALID ENDINGS
        # =====================
        for ending in Validator.INVALID_ENDINGS:
            if email.endswith(ending):
                return False

        # =====================
        # DOUBLE DOTS
        # =====================
        if ".." in email:
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