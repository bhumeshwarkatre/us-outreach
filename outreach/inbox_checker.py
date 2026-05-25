import email

from outreach.reply_classifier import (
    ReplyClassifier
)


class InboxChecker:

    def __init__(
        self,
        db,
        mailer
    ):

        self.db = db

        self.mailer = mailer

    def check_replies(self):

        mail = (
            self.mailer
            .get_inbox_connection()
        )

        if not mail:
            return []

        mail.select("inbox")

        _, messages = mail.search(
            None,
            "UNSEEN"
        )

        results = []

        for num in messages[0].split():

            _, data = mail.fetch(
                num,
                "(RFC822)"
            )

            raw_email = data[0][1]

            msg = email.message_from_bytes(
                raw_email
            )

            sender = msg["From"]

            subject = msg["Subject"]

            body = ""

            if msg.is_multipart():

                for part in msg.walk():

                    if (
                        part.get_content_type()
                        == "text/plain"
                    ):

                        body = (
                            part.get_payload(
                                decode=True
                            ).decode()
                        )

            else:

                body = (
                    msg.get_payload(
                        decode=True
                    ).decode()
                )

            interested = (
                ReplyClassifier
                .is_interested(body)
            )

            results.append({

                "sender": sender,

                "subject": subject,

                "body": body,

                "interested": interested
            })

        return results