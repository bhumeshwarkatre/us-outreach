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

        # Brevo SMTP login
        self.email_address = (
            EMAIL_ADDRESS
        )

        # Brevo SMTP key
        self.email_password = (
            EMAIL_PASSWORD
        )

        self.smtp_server = SMTP_SERVER

        self.smtp_port = SMTP_PORT

        self.imap_server = IMAP_SERVER

        # Actual visible sender
        self.sender_email = (
            "ggremedia.kazuki@gmail.com"
        )

    def send_email(

        self,

        recipient,
        subject,
        body
    ):

        try:

            msg = MIMEMultipart()

            # Visible sender
            msg["From"] = (
                self.sender_email
            )

            msg["To"] = recipient

            msg["Subject"] = subject

            msg.attach(
                MIMEText(body, "plain")
            )

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

            # Brevo authentication
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