import re
import time
import random
from urllib.parse import quote_plus

from playwright.sync_api import (
    sync_playwright
)


class SearchCollector:

    # =========================
    # STRICT EMAIL REGEX
    # =========================

    EMAIL_REGEX = (
        r'\b[a-zA-Z0-9._%+-]+'
        r'@[a-zA-Z0-9.-]+'
        r'\.[a-zA-Z]{2,}\b'
    )

    # =========================
    # INIT
    # =========================

    def __init__(self):

        self.playwright = (
            sync_playwright()
            .start()
        )

        self.browser = (
            self.playwright
            .chromium
            .launch(
                headless=False,
                slow_mo=80
            )
        )

        self.context = (
            self.browser
            .new_context(
                viewport={
                    "width": 1400,
                    "height": 900
                },
                locale="en-US",
                timezone_id="America/New_York"
            )
        )

        self.page = (
            self.context
            .new_page()
        )

    # =========================
    # HUMAN DELAY
    # =========================

    def human_delay(
        self,
        min_seconds=2,
        max_seconds=5
    ):

        time.sleep(
            random.uniform(
                min_seconds,
                max_seconds
            )
        )

    # =========================
    # HUMAN SCROLL
    # =========================

    def human_scroll(self):

        scroll_count = random.randint(2, 5)

        for _ in range(scroll_count):

            self.page.mouse.wheel(
                0,
                random.randint(
                    500,
                    1500
                )
            )

            self.human_delay(1, 3)

    # =========================
    # CAPTCHA DETECTION
    # =========================

    def is_captcha_page(self):

        try:

            body = (
                self.page
                .inner_text("body")
                .lower()
            )

            indicators = [

                "unusual traffic",

                "captcha",

                "not a robot",

                "recaptcha",

                "our systems have detected unusual traffic",

                "sorry"
            ]

            return any(
                item in body
                for item
                in indicators
            )

        except Exception:
            return False

    # =========================
    # CAPTCHA WAIT
    # =========================

    def wait_for_captcha(self):

        print(
            "\n[CAPTCHA DETECTED]"
        )

        print(
            "Solve captcha manually..."
        )

        while self.is_captcha_page():

            time.sleep(3)

        print(
            "[CAPTCHA CLEARED]"
        )

        return True

    # =========================
    # EXTRACT EMAILS
    # =========================

    # def extract_emails(
    #     self,
    #     text
    # ):

    #     if not text:
    #         return []

    #     emails = re.findall(
    #         self.EMAIL_REGEX,
    #         text
    #     )

    #     clean_emails = []

    #     blocked = [

    #         "example.com",

    #         "domain.com",

    #         "email.com",

    #         "yourname@",

    #         "@sentry",

    #         "@example"
    #     ]

    #     for email in emails:

    #         email = (
    #             email
    #             .lower()
    #             .strip()
    #         )

    #         # remove invalid
    #         if any(
    #             b in email
    #             for b in blocked
    #         ):
    #             continue

    #         # proper format check
    #         if "@" not in email:
    #             continue

    #         if "." not in email.split("@")[-1]:
    #             continue

    #         if email not in clean_emails:
    #             clean_emails.append(
    #                 email
    #             )

    #     return clean_emails

    def extract_emails(
        self,
        text
    ):

        if not text:
             return []

        emails = re.findall(
            self.EMAIL_REGEX,
            text
        )

        clean_emails = []

        blocked = [
            "example.com",
            "domain.com",
            "email.com",
            "yourname@",
            "@sentry",
            "@example"
        ]

        blocked_read = re.compile(
            r'\.read(\.|$)',
            re.IGNORECASE
        )

        for email in emails:

            email = (
                email
                .lower()
                .strip()
            )

            # remove invalid
            if any(
                b in email
                for b in blocked
            ):
                continue

            # block .read in domain
            domain = email.split("@")[-1]
            if blocked_read.search(domain):
                continue

            # proper format check
            if "@" not in email:
                continue

            if "." not in email.split("@")[-1]:
                continue

            if email not in clean_emails:
                clean_emails.append(
                    email
                )

        return clean_emails

    # =========================
    # EXTRACT NAME
    # =========================

    def extract_name(
        self,
        title,
        snippet
    ):

        combined = (
            f"{title} {snippet}"
        )

        combined = (
            combined
            .replace("|", " ")
            .replace("-", " ")
            .replace("•", " ")
        )

        parts = combined.split()

        if not parts:
            return "Unknown"

        name_parts = []

        for word in parts:

            clean = word.strip()

            # skip usernames
            if "@" in clean:
                continue

            # only text words
            if not clean.isascii():
                continue

            if len(clean) < 2:
                continue

            if clean.lower() in [
                "instagram",
                "photos",
                "videos",
                "gmail",
                "youtube"
            ]:
                continue

            if clean[0].isupper():

                name_parts.append(
                    clean
                )

            if len(name_parts) >= 2:
                break

        if not name_parts:
            return "Unknown"

        return " ".join(
            name_parts
        )

    # =========================
    # EXTRACT PAGE RESULTS
    # =========================

    def extract_current_page_results(
        self
    ):

        collected_results = []

        search_results = (
            self.page
            .query_selector_all(
                "div.g"
            )
        )

        if not search_results:

            search_results = (
                self.page
                .query_selector_all(
                    "div.tF2Cxc"
                )
            )

        for result in search_results:

            try:

                title = ""
                snippet = ""
                clean_url = ""
                platform = None

                # =====================
                # TITLE
                # =====================

                title_element = (
                    result.query_selector(
                        "h3"
                    )
                )

                if title_element:

                    title = (
                        title_element
                        .inner_text()
                        .strip()
                    )

                # =====================
                # SNIPPET
                # =====================

                snippet_selectors = [

                    ".VwiC3b",

                    ".yXK7lf",

                    ".MUxGbd",

                    ".lEBKkf"
                ]

                for selector in snippet_selectors:

                    try:

                        element = (
                            result
                            .query_selector(
                                selector
                            )
                        )

                        if element:

                            snippet = (
                                element
                                .inner_text()
                                .strip()
                            )

                            if snippet:
                                break

                    except Exception:
                        pass

                # =====================
                # LINK
                # =====================

                link_element = (
                    result.query_selector(
                        "a"
                    )
                )

                if not link_element:
                    continue

                href = (
                    link_element
                    .get_attribute(
                        "href"
                    )
                )

                if not href:
                    continue

                clean_url = href

                # =====================
                # PLATFORM FILTER
                # =====================

                if (
                    "instagram.com"
                    in clean_url
                ):

                    platform = "instagram"

                elif (
                    "youtube.com"
                    in clean_url
                ):

                    platform = "youtube"

                if not platform:
                    continue

                # =====================
                # FULL TEXT
                # =====================

                combined_text = (
                    f"{title} "
                    f"{snippet}"
                )

                # =====================
                # EMAIL EXTRACTION
                # =====================

                emails = (
                    self.extract_emails(
                        combined_text
                    )
                )

                # =====================
                # NAME EXTRACTION
                # =====================

                creator_name = (
                    self.extract_name(
                        title,
                        snippet
                    )
                )

                collected_results.append({

                    "creator_name":
                        creator_name,

                    "title":
                        title,

                    "snippet":
                        snippet,

                    "url":
                        clean_url,

                    "platform":
                        platform,

                    "emails":
                        emails
                })

            except Exception as error:

                print(
                    f"[RESULT ERROR] "
                    f"{error}"
                )

        return collected_results

    # =========================
    # SEARCH
    # =========================

    def search(
        self,
        query,
        max_pages=1
    ):

        google_url = (
            "https://www.google.com/search?q="
            f"{quote_plus(query)}"
        )

        all_results = []

        try:

            self.page.goto(
                google_url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            self.human_delay()

            # captcha
            if self.is_captcha_page():

                solved = (
                    self.wait_for_captcha()
                )

                if not solved:
                    return []

            current_page = 1

            while current_page <= max_pages:

                self.human_scroll()

                self.page.wait_for_timeout(
                    random.randint(
                        2000,
                        5000
                    )
                )

                page_results = (
                    self.extract_current_page_results()
                )

                all_results.extend(
                    page_results
                )

                if current_page >= max_pages:
                    break

                next_button = (
                    self.page.query_selector(
                        "#pnnext"
                    )
                )

                if not next_button:
                    break

                next_button.click()

                self.human_delay(3, 6)

                current_page += 1

            # =====================
            # REMOVE DUPLICATES
            # =====================

            unique_results = []

            seen = set()

            for item in all_results:

                unique_key = (
                    item["url"],
                    tuple(item["emails"])
                )

                if unique_key in seen:
                    continue

                seen.add(unique_key)

                unique_results.append(
                    item
                )

            return unique_results

        except Exception as error:

            print(
                f"[SEARCH ERROR] "
                f"{error}"
            )

            return []

    # =========================
    # CLOSE
    # =========================

    def close(self):

        try:
            self.page.close()
        except:
            pass

        try:
            self.context.close()
        except:
            pass

        try:
            self.browser.close()
        except:
            pass

        try:
            self.playwright.stop()
        except:
            pass