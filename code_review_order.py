"""Display order of code review pull requests for CP1404."""

USERNAMES_FILENAME = "data/github_usernames.txt"
OUTPUT_FILENAME = "output/code_reviews.md"
FIRST_PRAC = 5  # 5 at start of study period
LAST_PRAC = 10


def main():
    """Create code review orders as text for CP1404 pull requests."""
    print("# CP1404 Code Reviews")
    with open(USERNAMES_FILENAME) as in_file:
        usernames = [line.strip() for line in in_file.readlines()]
    max_length = max(len(username) for username in usernames)

    with open(OUTPUT_FILENAME, "w") as out_file:
        for i in range(0, LAST_PRAC - FIRST_PRAC + 1):
            print(f"\n## Prac {i + FIRST_PRAC}:", file=out_file)
            print("\n```", file=out_file)
            for position, username in enumerate(usernames):
                other_username = usernames[position - (i + 1)]
                print(f"{username:{max_length}} mentions:  {other_username}", file=out_file)
            print("```", file=out_file)


if __name__ == '__main__':
    main()
