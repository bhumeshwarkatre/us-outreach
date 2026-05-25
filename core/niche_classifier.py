import json


class NicheClassifier:

    def __init__(self):

        with open(
            "config/niches.json",
            "r"
        ) as file:

            self.niches = json.load(file)

    def classify(self, text):

        text = text.lower()

        for niche, keywords in self.niches.items():

            for keyword in keywords:

                if keyword.lower() in text:
                    return niche

        return None