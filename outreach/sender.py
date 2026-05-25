import random
import time

from outreach.templates import (
    INITIAL_TEMPLATE
)


class OutreachSender:

    def __init__(self, db, mailer):

        self.db = db
        self.mailer = mailer

    def send_to_lead(self, lead):

        try:

            body = INITIAL_TEMPLATE.format(
                name=lead["creator_name"]
            )

            success = self.mailer.send_email(

                recipient=lead["email"],

                subject=(
                    "Custom Monetization "
                    "Strategy For Your Content"
                ),

                body=body
            )

            if success:

                query = """
                UPDATE leads
                SET status = ?
                WHERE id = ?
                """

                self.db.cursor.execute(
                    query,
                    (
                        "sent",
                        lead["id"]
                    )
                )

                self.db.conn.commit()

                print(
                    f"[SENT] {lead['email']}"
                )

                time.sleep(
                    random.randint(10, 30)
                )

                return True

            return False

        except Exception as error:

            print(
                f"[SENDER ERROR] {error}"
            )

            return False

    def send_bulk(self, leads):

        sent_count = 0

        for lead in leads:

            success = self.send_to_lead(
                lead
            )

            if success:
                sent_count += 1

        return sent_count