import requests
from bs4 import BeautifulSoup

from config.settings import (
    HEADERS,
    REQUEST_TIMEOUT
)


class ProfileExtractor:

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update(
            HEADERS
        )

    def extract(self, url):

        try:

            response = self.session.get(
                url,
                timeout=REQUEST_TIMEOUT
            )

            soup = BeautifulSoup(
                response.text,
                "lxml"
            )

            title = soup.title.text.strip()

            text = soup.get_text(
                separator=" "
            )

            return {
                "url": url,
                "title": title,
                "content": text[:5000]
            }

        except Exception as error:

            print(
                f"[PROFILE ERROR] {error}"
            )

            return None