from .mail import compose, send

def main():
    mail = compose.create_newsletter(None)
    print("newsletter created!")

    recipients = send.send_mail(mail.plain_text, mail.html_text, mail.date)
    print("email sent to", recipients)


if __name__ == "__main__":
    main()
