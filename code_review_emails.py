"""
Check sets of emails for missing or incorrect students
for code review order making
"""

ALL_FILENAME = 'data/emails_all.txt'
SUBMITTED_FILENAME = 'data/emails_submitted.txt'


def main():
    """Program to load emails and determine missing or incorrect students."""
    submitted_emails = load_emails(SUBMITTED_FILENAME)
    all_class_emails = load_emails(ALL_FILENAME)
    missing_emails = all_class_emails - submitted_emails
    print(f"{len(missing_emails)} Missing: ")
    print("\n".join(missing_emails))
    print("\nIncorrect or withdrawn: ")
    print("\n".join(submitted_emails - all_class_emails))


def load_emails(filename):
    """Load text file of emails (one per line) and return set."""
    with open(filename, 'r') as in_file:
        text = in_file.read()
    return set(text.lower().strip().split())


if __name__ == '__main__':
    main()
