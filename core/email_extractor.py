# import re


# class EmailExtractor:

#     EMAIL_REGEX = (
#         r'[a-zA-Z0-9._%+-]+'
#         r'@[a-zA-Z0-9.-]+'
#         r'\\.[a-zA-Z]{2,}'
#     )

#     @classmethod
#     def extract(cls, text):

#         emails = re.findall(
#             cls.EMAIL_REGEX,
#             text
#         )

#         clean_emails = []

#         for email in emails:

#             email = email.lower().strip()

#             if email not in clean_emails:
#                 clean_emails.append(email)

#         return clean_emails


# import re


# class EmailExtractor:

#     EMAIL_REGEX = re.compile(
#         r'[a-zA-Z0-9._%+-]+'
#         r'@[a-zA-Z0-9.-]+'
#         r'\.[a-zA-Z]{2,}'
#     )

#     @classmethod
#     def extract(cls, text):

#         if not text:
#             return []

#         raw_emails = re.findall(cls.EMAIL_REGEX, text)

#         clean_emails = []

#         for email in raw_emails:

#             email = email.lower().strip()

#             # 🔥 HARD CLEANING (IMPORTANT)
#             email = email.replace(".read", "")
#             email = email.replace("read", "")

#             # remove invalid trailing dots
#             email = email.strip(".")

#             # final safety check (prevents garbage)
#             if cls.is_valid(email) and email not in clean_emails:
#                 clean_emails.append(email)

#         return clean_emails

#     @staticmethod
#     def is_valid(email):

#         pattern = re.compile(
#             r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#         )

#         return bool(pattern.match(email))

import re


class EmailExtractor:

    EMAIL_REGEX = re.compile(
        r'[a-zA-Z0-9._%+-]+'
        r'@[a-zA-Z0-9.-]+'
        r'\.[a-zA-Z]{2,}'
    )

    BLOCKED_PATTERNS = re.compile(r'\.read(\.|$)', re.IGNORECASE)

    @classmethod
    def extract(cls, text):
        if not text:
            return []

        raw_emails = re.findall(cls.EMAIL_REGEX, text)
        clean_emails = []

        for email in raw_emails:
            email = email.lower().strip().strip(".")

            if (
                cls.is_valid(email)
                and not cls.has_blocked_pattern(email)
                and email not in clean_emails
            ):
                clean_emails.append(email)

        return clean_emails

    @classmethod
    def has_blocked_pattern(cls, email):
        """Block .read anywhere in the domain part."""
        domain = email.split("@")[-1]          # everything after @
        return bool(cls.BLOCKED_PATTERNS.search(domain))

    @staticmethod
    def is_valid(email):
        pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        return bool(pattern.match(email))