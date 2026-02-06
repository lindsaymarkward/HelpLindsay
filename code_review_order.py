"""Display order of code review pull requests for CP1404."""
import re

USERNAMES_FILENAME = "data/github_usernames_b.txt"
OUTPUT_FILENAME = "output/code_reviews.md"
FIRST_PRAC = 5  # 5 at start of study period
LAST_PRAC = 9


def main():
    """Create code review orders as text for CP1404 pull requests."""
    print("# CP1404 Code Reviews")
    with open(USERNAMES_FILENAME) as in_file:
        usernames = [line.strip() for line in in_file.readlines()]

    # Find problems in the usernames list, stopping
    duplicates = find_duplicates(usernames)
    if duplicates:
        print(f"Duplicate usernames found: {duplicates}\nStopping.")
        return
    invalid_usernames = find_invalids(usernames)
    if invalid_usernames:
        print(f"Invalid usernames found: {invalid_usernames}\nStopping.")
        return

    max_length = max(len(username) for username in usernames)

    with open(OUTPUT_FILENAME, "w") as out_file:
        for i in range(0, LAST_PRAC - FIRST_PRAC + 1):
            print(f"\n## Prac {i + FIRST_PRAC}", file=out_file)
            print("\n```", file=out_file)
            for position, username in enumerate(usernames):
                other_username = usernames[position - (i + 1)]
                print(f"{username:{max_length}} mentions:  {other_username}", file=out_file)
            print("```", file=out_file)
    print(f"See Markdown file: {OUTPUT_FILENAME}")


def find_duplicates(usernames):
    """Find and return duplicates in the usernames list."""
    duplicates = set([username for username in usernames if usernames.count(username) > 1])
    return duplicates


def find_invalids(usernames):
    """
    Find and return list of all invalid usernames.
    - Only alphanumeric characters or hyphens
    - No consecutive hyphens
    - Cannot begin or end with a hyphen
    - Maximum length: 39 characters
    """
    pattern = re.compile(r'^(?!-)(?!.*--)[A-Za-z0-9-]{1,39}(?<!-)$')
    return [username for username in usernames if not pattern.match(username)]


if __name__ == '__main__':
    main()
