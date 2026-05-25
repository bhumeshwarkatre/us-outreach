US_KEYWORDS = [

    "usa",
    "united states",

    "new york",
    "los angeles",
    "miami",
    "chicago",
    "houston",
    "dallas",
    "austin",
    "california",
    "texas",
    "florida",
    "seattle",
    "boston"
]


class CountryDetector:

    @staticmethod
    def detect(text):

        text = text.lower()

        for keyword in US_KEYWORDS:

            if keyword in text:
                return "USA"

        return None