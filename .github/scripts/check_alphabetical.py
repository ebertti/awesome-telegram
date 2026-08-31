#!/usr/bin/env python3
"""
Checks that every contiguous block of README list entries (`* [Name](link) – ...`)
is sorted alphabetically, case-insensitive, ignoring a leading `@`.

Blocks separated only by blank lines are treated as one block (a single section's
list), so a blank line between two entries does not exempt them from the check.

Usage: check_alphabetical.py [README.md]
Exits 1 and prints the offending lines if anything is out of order.
"""

import re
import sys

ENTRY_RE = re.compile(r'^(\s*)\* \[(.+?)\]')


def sort_key(line: str) -> str:
    m = ENTRY_RE.match(line)
    return m.group(2).lstrip('@').lower()


def find_out_of_order(lines: list[str]):
    problems = []
    i = 0
    n = len(lines)
    while i < n:
        if ENTRY_RE.match(lines[i]):
            j = i
            block = []
            while j < n:
                if ENTRY_RE.match(lines[j]):
                    block.append((j, lines[j]))
                    j += 1
                elif lines[j].strip() == "" and j + 1 < n and ENTRY_RE.match(lines[j + 1]):
                    j += 1
                else:
                    break
            keys = [sort_key(l) for _, l in block]
            for k in range(1, len(keys)):
                if keys[k] < keys[k - 1]:
                    problems.append((block[k][0] + 1, block[k][1].strip(), block[k - 1][1].strip()))
            i = j
        else:
            i += 1
    return problems


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "README.md"
    with open(path) as f:
        lines = f.readlines()

    problems = find_out_of_order(lines)
    if problems:
        print(f"Alphabetical order issues found ({len(problems)}):")
        for lineno, entry, prev in problems:
            print(f"  line {lineno}: {entry[:100]}")
            print(f"    sorts before the previous entry: {prev[:100]}")
        sys.exit(1)
    else:
        print("Alphabetical order OK.")


if __name__ == "__main__":
    main()
