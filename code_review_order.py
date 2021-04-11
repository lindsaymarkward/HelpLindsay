"""Display order of code review pull requests for CP1404 EXT."""

USERNAMES_FILE = "data/github_usernames.txt"
FIRST_PRAC = 5  # 5 at start of study period
LAST_PRAC = 10


def main():
    """Create code review orders as text for CP1404 pull requests."""
    print("# CP1404 External Code Reviews")
    with open(USERNAMES_FILE) as in_file:
        usernames = [line.strip() for line in in_file.readlines()]
    max_length = max(len(username) for username in usernames)

    for i in range(0, LAST_PRAC - FIRST_PRAC + 1):
        print("## Prac {}:".format(i + FIRST_PRAC))
        print("```")
        for position, username in enumerate(usernames):
            other_username = usernames[position - (i + 1)]
            print(f"{username:{max_length}} mentions:  {other_username}")
        print("```")


if __name__ == '__main__':
    main()
