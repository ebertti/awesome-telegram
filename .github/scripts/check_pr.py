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
NAME_RE = re.compile(r'^\* \[(.+?)\]')

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


def sort_key(entry: str) -> str:
    m = NAME_RE.match(entry)
    return m.group(1).lstrip('@').lower()


def get_added_entries_with_neighbors(diff: str) -> list[dict]:
    """For each added README entry, returns its immediate prev/next sibling
    entry as they appear in the resulting file, reconstructed from the diff's
    own context lines (no need to check out the PR head)."""
    results = []
    hunk_lines: list[str] = []

    def flush():
        if not hunk_lines:
            return
        # Lines present in the final file, in order, within this hunk.
        final_lines = [l[1:] for l in hunk_lines if l[0] in (' ', '+')]
        final_idx = 0
        for l in hunk_lines:
            if l[0] not in (' ', '+'):
                continue
            if l[0] == '+' and ENTRY_RE.match(l[1:].strip()):
                prev_entry = None
                k = final_idx - 1
                while k >= 0 and final_lines[k].strip() == "":
                    k -= 1
                if k >= 0 and ENTRY_RE.match(final_lines[k].strip()):
                    prev_entry = final_lines[k].strip()

                next_entry = None
                k = final_idx + 1
                while k < len(final_lines) and final_lines[k].strip() == "":
                    k += 1
                if k < len(final_lines) and ENTRY_RE.match(final_lines[k].strip()):
                    next_entry = final_lines[k].strip()

                results.append({
                    "content": l[1:].strip(),
                    "prev": prev_entry,
                    "next": next_entry,
                })
            final_idx += 1

    for line in diff.splitlines():
        if line.startswith("@@"):
            flush()
            hunk_lines = []
        elif line.startswith("+++") or line.startswith("---"):
            continue
        elif line[:1] in (' ', '+', '-'):
            hunk_lines.append(line)
    flush()
    return results


def check_order(entry: str, prev: str | None, next_: str | None) -> list[str]:
    """Checks the entry sorts between its immediate diff-context neighbors
    (case-insensitive, ignoring a leading @). Only flags issues we can
    determine directly from the PR's own diff context."""
    issues = []
    try:
        key = sort_key(entry)
    except AttributeError:
        return issues
    if prev is not None:
        try:
            if key < sort_key(prev):
                issues.append(f"should come **before** `{prev[:100]}`, not after it")
        except AttributeError:
            pass
    if next_ is not None:
        try:
            if key > sort_key(next_):
                issues.append(f"should come **after** `{next_[:100]}`, not before it")
        except AttributeError:
            pass
    return issues


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
    order_issues: list[tuple[str, list[str]]] = []

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

    for item in get_added_entries_with_neighbors(diff):
        order = check_order(item["content"], item["prev"], item["next"])
        if order:
            order_issues.append((item["content"], order))

    if not format_issues and not url_issues and not order_issues:
        body = (
            "<!-- awesome-telegram-check -->\n"
            "## ✅ PR Check Passed\n\n"
            "All added entries follow the correct format, are in alphabetical order, and links are reachable. "
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

    if order_issues:
        lines.append("### Alphabetical Order\n")
        lines.append("Entries must be inserted in alphabetical order within their section (case-insensitive, ignoring a leading `@`).\n")
        for entry, issues in order_issues:
            lines.append(f"**Line:** `{entry}`")
            for issue in issues:
                lines.append(f"- {issue}")
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
