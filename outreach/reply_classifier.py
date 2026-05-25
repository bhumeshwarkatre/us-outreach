POSITIVE_KEYWORDS = [

    "interested",
    "yes",
    "sure",
    "sounds good",
    "tell me more",
    "i am interested",
    "let's do it"
]


class ReplyClassifier:

    @staticmethod
    def is_interested(text):

        text = text.lower()

        for keyword in POSITIVE_KEYWORDS:

            if keyword in text:
                return True

        return False