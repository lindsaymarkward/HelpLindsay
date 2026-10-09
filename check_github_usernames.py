"""
Validate GitHub usernames using the GitHub REST API.
Reads usernames from a text file and writes validation results to a CSV file.
Requires a GitHub token in the GITHUB_TOKEN environment variable (PyCharm run configuration).
(Written by ChatGPT)
"""

import csv
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import quote

INPUT_FILE = Path("data/github_usernames_a.txt")
OUTPUT_FILE = Path("output/github_username_results.csv")
API_URL = "https://api.github.com/users/"
REQUEST_TIMEOUT = 15
REQUEST_DELAY = 0.2

CSV_FIELDS = [
    "username",
    "status",
    "canonical_username",
    "profile_url",
    "details",
]


def main() -> None:
    """Validate usernames and save the results to a CSV file."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit(
            "GITHUB_TOKEN is not set. Set it in Terminal before running."
        )

    if not INPUT_FILE.exists():
        raise SystemExit(f"Input file not found: {INPUT_FILE}")

    usernames = read_usernames(INPUT_FILE)
    previous_results = read_previous_results(OUTPUT_FILE)
    results = dict(previous_results)

    for index, username in enumerate(usernames, start=1):
        previous = results.get(username)

        # Reuse successful checks; retry previous errors.
        if previous and previous["status"] in {"Valid", "Not found"}:
            print(f"{index}/{len(usernames)}: {username} -> cached")
            continue

        result = check_username(username, token)
        results[username] = result

        print(f"{index}/{len(usernames)}: {username} -> {result['status']}")
        if result["details"]:
            print(f"    {result['details']}")

        write_results(OUTPUT_FILE, usernames, results)

        if result["status"] == "Error":
            # Stop rather than repeatedly hitting a rate limit.
            if "rate limit" in result["details"].lower():
                print("Rate limit encountered; stopping to avoid more errors.")
                break

        time.sleep(REQUEST_DELAY)

    write_results(OUTPUT_FILE, usernames, results)
    print_summary(usernames, results)
    print(f"\nResults saved to: {OUTPUT_FILE.resolve()}")


def read_usernames(path: Path) -> list[str]:
    """Read usernames from plain text or a Markdown table.

    Remove blank lines, table separators, and duplicate usernames while
    preserving the original order.
    """
    usernames = []

    for line in path.read_text(encoding="utf-8-sig").splitlines():
        username = line.strip().strip("|").strip()

        if not username or set(username) <= {"-", " "}:
            continue
        if username.lower() in {"username", "usernames"}:
            continue
        if "|" in username:
            continue

        usernames.append(username)

    return list(dict.fromkeys(usernames))


def read_previous_results(path: Path) -> dict[str, dict[str, str]]:
    """Load existing CSV results, returning an empty dictionary if absent."""
    if not path.exists():
        return {}

    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return {
            row["username"]: row
            for row in reader
            if row.get("username") and row.get("status")
        }


def check_username(username: str, token: str) -> dict[str, str]:
    """Check whether a public GitHub account exists for a username."""
    url = API_URL + quote(username, safe="")
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "GitHub-Username-Validator",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    try:
        with urllib.request.urlopen(
                request, timeout=REQUEST_TIMEOUT
        ) as response:
            data: dict[str, Any] = json.load(response)

        return {
            "username": username,
            "status": "Valid",
            "canonical_username": data.get("login", ""),
            "profile_url": data.get("html_url", ""),
            "details": "",
        }

    except urllib.error.HTTPError as error:
        if error.code == 404:
            status = "Not found"
            details = "No account found for this username"
        elif error.code == 401:
            status = "Error"
            details = "Token invalid or rejected; check GITHUB_TOKEN"
        elif error.code in {403, 429}:
            status = "Error"
            remaining = error.headers.get("X-RateLimit-Remaining", "")
            reset = error.headers.get("X-RateLimit-Reset", "")
            details = (
                f"Rate limit or access restriction "
                f"(remaining={remaining}, reset={reset})"
            )
        else:
            status = "Error"
            details = f"HTTP {error.code}"

        return make_result(username, status, details)

    except (OSError, TimeoutError, ValueError) as error:
        return make_result(username, "Error", str(error))


def make_result(
        username: str, status: str, details: str
) -> dict[str, str]:
    """Create a consistently structured result row."""
    return {
        "username": username,
        "status": status,
        "canonical_username": "",
        "profile_url": "",
        "details": details,
    }


def write_results(
        path: Path,
        usernames: list[str],
        results: dict[str, dict[str, str]],
) -> None:
    """Write available results in the original input order."""
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for username in usernames:
            if username in results:
                writer.writerow(results[username])


def print_summary(
        usernames: list[str], results: dict[str, dict[str, str]]
) -> None:
    """Print counts of completed, failed, and pending checks."""
    print("\nSummary")

    for status in ("Valid", "Not found", "Error"):
        count = sum(
            results.get(username, {}).get("status") == status
            for username in usernames
        )
        print(f"{status}: {count}")

    pending = sum(username not in results for username in usernames)
    print(f"Pending: {pending}")


if __name__ == "__main__":
    main()
