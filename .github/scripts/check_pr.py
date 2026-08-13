#!/usr/bin/env python3
"""
Validates README entries added in a PR:
- Format: * [Name](https://url) – Single sentence description.
- URLs: reachable (HTTP 200/301/302)
Posts a comment on the PR if issues are found.
"""

import os
import re
import sys
import json
import urllib.request
import urllib.error

README_PATTERN = re.compile(r'^\* \[.+?\]\((https?://[^\)]+)\) – .+\.$')
ENTRY_RE = re.compile(r'^\* \[')

HEADERS = {"User-Agent": "awesome-telegram-bot/1.0"}


def get_added_entries(diff: str) -> list[tuple[int, str]]:
    """Returns (line_number_approx, content) for added README list entries."""
    entries = []
    line_num = 0
    for line in diff.splitlines():
        if line.startswith("@@"):
            # extract starting line from hunk header
            m = re.search(r'\+(\d+)', line)
            if m:
                line_num = int(m.group(1)) - 1
        elif line.startswith("+"):
            line_num += 1
            content = line[1:]
            if ENTRY_RE.match(content.strip()):
                entries.append((line_num, content.strip()))
        elif not line.startswith("-"):
            line_num += 1
    return entries


def check_format(entry: str) -> list[str]:
    issues = []
    if not README_PATTERN.match(entry):
        if " - " in entry and " – " not in entry:
            issues.append("uses `-` instead of `–` (en dash)")
        elif " — " in entry:
            issues.append("uses `—` (em dash) instead of `–` (en dash)")
        elif not entry.endswith("."):
            issues.append("description must end with a period `.`")
        elif not re.search(r'– .', entry):
            issues.append("missing `–` separator between link and description")
        else:
            issues.append("does not match the expected format: `* [Name](https://url) – Description.`")
    return issues


def check_url(url: str, timeout: int = 10) -> tuple[bool, str]:
    req = urllib.request.Request(url, headers=HEADERS, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        if e.code in (405, 403):
            # HEAD not allowed — try GET
            try:
                req2 = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req2, timeout=timeout) as resp:
                    return True, f"HTTP {resp.status}"
            except Exception as e2:
                return False, str(e2)
        return False, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return False, str(e.reason)
    except Exception as e:
        return False, str(e)


def post_comment(token: str, repo: str, pr_number: str, body: str):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    data = json.dumps({"body": body}).encode()
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def update_comment(token: str, comment_id: int, repo: str, body: str):
    url = f"https://api.github.com/repos/{repo}/issues/comments/{comment_id}"
    data = json.dumps({"body": body}).encode()
    req = urllib.request.Request(
        url, data=data, method="PATCH",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def find_existing_bot_comment(token: str, repo: str, pr_number: str) -> int | None:
    """Returns comment_id of a previous bot check comment, if any."""
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments?per_page=100"
    req = urllib.request.Request(
        url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )
    with urllib.request.urlopen(req) as resp:
        comments = json.loads(resp.read())
    for c in comments:
        if c["user"]["login"] == "github-actions[bot]" and "<!-- awesome-telegram-check -->" in c["body"]:
            return c["id"]
    return None


def main():
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]
    diff_file = os.environ.get("DIFF_FILE", "pr.diff")

    with open(diff_file) as f:
        diff = f.read()

    entries = get_added_entries(diff)

    if not entries:
        print("No README list entries found in diff. Skipping.")
        sys.exit(0)

    format_issues: list[tuple[str, list[str]]] = []
    url_issues: list[tuple[str, str, str]] = []

    for _lineno, entry in entries:
        fmt = check_format(entry)
        if fmt:
            format_issues.append((entry, fmt))

        url_match = re.search(r'\((https?://[^\)]+)\)', entry)
        if url_match:
            url = url_match.group(1)
            ok, detail = check_url(url)
            if not ok:
                url_issues.append((entry, url, detail))

    if not format_issues and not url_issues:
        body = (
            "<!-- awesome-telegram-check -->\n"
            "## ✅ PR Check Passed\n\n"
            "All added entries follow the correct format and links are reachable. "
            "Thanks for the contribution!"
        )
        existing = find_existing_bot_comment(token, repo, pr_number)
        if existing:
            update_comment(token, existing, repo, body)
        else:
            post_comment(token, repo, pr_number, body)
        print("All checks passed.")
        sys.exit(0)

    # Build comment body
    lines = ["<!-- awesome-telegram-check -->", "## ❌ PR Check — Issues Found", ""]
    lines.append("Thanks for the contribution! Please fix the following before we can merge:\n")

    if format_issues:
        lines.append("### Format Issues\n")
        lines.append("Expected format: `* [Name](https://url) – Single sentence description.`\n")
        for entry, issues in format_issues:
            lines.append(f"**Line:** `{entry}`")
            for issue in issues:
                lines.append(f"- {issue}")
            lines.append("")

    if url_issues:
        lines.append("### Unreachable Links\n")
        for entry, url, detail in url_issues:
            lines.append(f"**Line:** `{entry}`")
            lines.append(f"- URL `{url}` returned: `{detail}`")
            lines.append("")

    lines.append("---")
    lines.append("_This check runs automatically on every push to this PR._")

    body = "\n".join(lines)

    existing = find_existing_bot_comment(token, repo, pr_number)
    if existing:
        update_comment(token, existing, repo, body)
        print(f"Updated existing comment {existing}.")
    else:
        post_comment(token, repo, pr_number, body)
        print("Posted new comment.")

    sys.exit(1)


if __name__ == "__main__":
    main()
