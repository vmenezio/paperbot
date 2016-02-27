from .mail import compose

def main():
    newsletter = compose.create_newsletter(None)

    print("HTML:", newsletter.html, sep="\n")
    print("TEXT:", newsletter.text, sep="\n")
    print(newsletter.date)


if __name__ == "__main__":
    main()
