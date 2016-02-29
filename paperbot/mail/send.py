import os
import json
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

DATA = os.path.dirname(__file__)+"/data/"

def send_mail(plain_text, html_text, date, credentials_json=DATA+"creds.json",
        recipients_json=DATA+"recips.json"):
    """Sends an email via gmail.

    Build an email out of the plain text and html versions recieved,
    logs into gmail with the credentials found in the credentials.json
    file and sends the message to the contacts specified in the
    recipients.json file.
    """
    credentials = get_credentials(credentials_json)
    recipients = get_recipients(recipients_json)

    message = MIMEMultipart('alternative')
    message['From'] = "PaperBot <"+credentials["username"]+">"
    message['To'] = ", ".join(recipients)
    message['Subject'] = "The Weekly Droid - " + date

    message.attach(MIMEText(plain_text, 'plain'))
    message.attach(MIMEText(html_text, 'html', 'utf-8'))

    send_mime_message(message, credentials, recipients)

    return recipients

def send_mime_message(message, credentials, recipients):
    """Send a message via the gmail SMTP server."""
    with SMTP("smtp.gmail.com", 587) as mail_server:
        mail_server.starttls()
        mail_server.login(credentials["username"], credentials["password"])
        mail_server.sendmail(credentials["username"], recipients,
            message.as_string())

def get_credentials(credentials_json):
    """Retrieve gmail login and password from external json file."""
    with open(credentials_json) as credentials_file:
        credentials = json.loads(credentials_file.read())
    return credentials

def get_recipients(recipients_json):
    """Return a list of recipients from external json file."""
    with open(recipients_json) as recipients_file:
        recipients = json.loads(recipients_file.read())
    return recipients
