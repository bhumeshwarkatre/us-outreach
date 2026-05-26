# import smtplib
# import imaplib

# from email.mime.text import MIMEText

# from email.mime.multipart import (
#     MIMEMultipart
# )

# from config.settings import (

#     EMAIL_ADDRESS,
#     EMAIL_PASSWORD,

#     SMTP_SERVER,
#     SMTP_PORT,

#     IMAP_SERVER
# )


# class Mailer:

#     def __init__(self):

#         self.email_address = (
#             EMAIL_ADDRESS
#         )

#         self.email_password = (
#             EMAIL_PASSWORD
#         )

#         self.smtp_server = SMTP_SERVER

#         self.smtp_port = SMTP_PORT

#         self.imap_server = IMAP_SERVER

#     def send_email(

#         self,

#         recipient,
#         subject,
#         body
#     ):

#         try:

#             msg = MIMEMultipart()

#             msg["From"] = (
#                 self.email_address
#             )

#             msg["To"] = recipient

#             msg["Subject"] = subject

#             msg.attach(
#                 MIMEText(body, "plain")
#             )

#             server = smtplib.SMTP(

#                 self.smtp_server,
#                 self.smtp_port
#             )

#             print("SMTP SERVER:", self.smtp_server)

#             server.set_debuglevel(1)

#             server.starttls()

#             server.login(

#                 self.email_address,
#                 self.email_password
#             )

#             server.send_message(msg)

#             server.quit()

#             return True

#         except Exception as error:

#             print(
#                 f"[MAIL ERROR] {error}"
#             )

#             return False

#     def get_inbox_connection(self):

#         try:

#             mail = imaplib.IMAP4_SSL(
#                 self.imap_server
#             )

#             mail.login(

#                 self.email_address,
#                 self.email_password
#             )

#             return mail

#         except Exception as error:

#             print(
#                 f"[IMAP ERROR] {error}"
#             )

#             return None


# import smtplib
# import imaplib

# from email.mime.text import MIMEText

# from email.mime.multipart import (
#     MIMEMultipart
# )

# from config.settings import (

#     EMAIL_ADDRESS,
#     EMAIL_PASSWORD,

#     SMTP_SERVER,
#     SMTP_PORT,

#     IMAP_SERVER
# )


# class Mailer:

#     def __init__(self):

#         # Brevo SMTP login
#         self.email_address = (
#             EMAIL_ADDRESS
#         )

#         # Brevo SMTP key
#         self.email_password = (
#             EMAIL_PASSWORD
#         )

#         self.smtp_server = SMTP_SERVER

#         self.smtp_port = SMTP_PORT

#         self.imap_server = IMAP_SERVER

#         # Actual visible sender
#         self.sender_email = (
#             "ggremedia.kazuki@gmail.com"
#         )

#     def send_email(

#         self,

#         recipient,
#         subject,
#         body
#     ):

#         try:

#             msg = MIMEMultipart()

#             # Visible sender
#             msg["From"] = (
#                 self.sender_email
#             )

#             msg["To"] = recipient

#             msg["Subject"] = subject

#             msg.attach(
#                 MIMEText(body, "plain")
#             )

#             server = smtplib.SMTP(

#                 self.smtp_server,
#                 self.smtp_port
#             )

#             print(
#                 "SMTP SERVER:",
#                 self.smtp_server
#             )

#             # server.set_debuglevel(1)

#             server.starttls()

#             # Brevo authentication
#             server.login(

#                 self.email_address,
#                 self.email_password
#             )

#             server.send_message(msg)

#             server.quit()

#             return True

#         except Exception as error:

#             print(
#                 f"[MAIL ERROR] {error}"
#             )

#             return False

#     def get_inbox_connection(self):

#         try:

#             mail = imaplib.IMAP4_SSL(
#                 self.imap_server
#             )

#             mail.login(

#                 self.sender_email,
#                 self.email_password
#             )

#             return mail

#         except Exception as error:

#             print(
#                 f"[IMAP ERROR] {error}"
#             )

#             return None

import smtplib
import imaplib

from email.mime.text import MIMEText

from email.mime.multipart import (
    MIMEMultipart
)

from config.settings import (

    EMAIL_ADDRESS,
    EMAIL_PASSWORD,

    SMTP_SERVER,
    SMTP_PORT,

    IMAP_SERVER
)


class Mailer:

    def __init__(self):

        # ✅ Google SMTP login (must match sender_email)
        self.email_address = (
            EMAIL_ADDRESS
        )

        # Google App Password
        self.email_password = (
            EMAIL_PASSWORD
        )

        self.smtp_server = SMTP_SERVER

        self.smtp_port = SMTP_PORT

        self.imap_server = IMAP_SERVER

        #  Visible sender MUST match EMAIL_ADDRESS for Gmail
        self.sender_email = (
            EMAIL_ADDRESS  
        )

    def send_email(

        self,

        recipient,
        subject,
        body
    ):

        try:

            # ✅ MIMEMultipart with "alternative" for plain + HTML
            msg = MIMEMultipart("alternative")

            # Visible sender (must match authenticated account)
            msg["From"] = (
                self.sender_email
            )

            msg["To"] = recipient

            msg["Subject"] = subject

            # ✅ REQUIRED: Plain-text part first (SpamAssassin priority)
            plain_body = body.strip()
            msg.attach(
                MIMEText(plain_body, "plain", "utf-8")
            )

            # ✅ Optional: Minimal HTML version (same content)
            html_body = (
                "<html><body><p>"
                + plain_body.replace("\n", "<br>")
                + "</p></body></html>"
            )
            msg.attach(
                MIMEText(html_body, "html", "utf-8")
            )

            # ✅ REQUIRED: List-Unsubscribe header (mass-email compliance)
            msg["List-Unsubscribe"] = (
                "<mailto:unsubscribe@yourdomain.com?subject=unsubscribe>"
            )
            msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

            server = smtplib.SMTP(

                self.smtp_server,
                self.smtp_port
            )

            print(
                "SMTP SERVER:",
                self.smtp_server
            )

            # server.set_debuglevel(1)

            server.starttls()

            # ✅ Google authentication
            server.login(

                self.email_address,
                self.email_password
            )

            server.send_message(msg)

            server.quit()

            return True

        except Exception as error:

            print(
                f"[MAIL ERROR] {error}"
            )

            return False

    def get_inbox_connection(self):

        try:

            mail = imaplib.IMAP4_SSL(
                self.imap_server
            )

            mail.login(

                self.sender_email,
                self.email_password
            )

            return mail

        except Exception as error:

            print(
                f"[IMAP ERROR] {error}"
            )

            return None