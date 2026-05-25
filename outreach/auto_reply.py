from outreach.templates import (
    REPLY_TEMPLATE
)


class AutoReply:

    def __init__(
        self,
        db,
        mailer
    ):

        self.db = db

        self.mailer = mailer

    def send_reply(

        self,

        recipient,
        creator_name
    ):

        body = REPLY_TEMPLATE.format(
            name=creator_name
        )

        success = self.mailer.send_email(

            recipient=recipient,

            subject=(
                "Next Steps "
                "For Monetization"
            ),

            body=body
        )

        return success