# CLAUDE.md — Guidelines for AI Agents (awesome-telegram)

This file provides instructions for Claude and other AI agents when reviewing pull requests, evaluating contributions, or helping maintain this repository.

---

## Purpose of this list

A curated collection of Telegram-related resources: bots, libraries, tools, groups, channels, and integrations. The key criterion is **relevance to Telegram** — not exclusivity. Multi-platform tools are welcome as long as they have meaningful Telegram support.

---

## Acceptance Criteria

### ✅ Accept if:
- The entry is related to Telegram in some way (bots, libraries, tools, integrations, channels, groups)
- It has a valid link (t.me, GitHub, website, etc.)
- The description is a single concise sentence
- It follows the formatting rules below
- It is placed at the bottom of the correct section

### ⚠️ Request changes if:
- The description is missing, vague, or marketing-heavy
- The description is longer than one sentence
- The format uses `-` instead of `–` (em dash)
- The entry is not placed at the bottom of the relevant section
- The PR title is "Update README.md" or similarly generic
- A link is missing (ask for project page, t.me, or website)
- The bot handle does not match the project branding

### ❌ Close/Reject if:
- The entry provides access to copyright-infringing content (e.g., unlicensed streaming links)
- The entry is a crypto trading bot that requests API keys via Telegram (security risk)
- The content appears to be self-promotion of paid/adult/gated content groups
- The PR title explicitly violates contributing guidelines (e.g., "Update README.md" adding low-quality content)

### Notes:
- **Public source code is NOT required** — closed-source bots and tools are welcome
- **Multi-platform tools are welcome** — if Telegram is one of several supported platforms, place the entry in `## Multi-platform Tools`
- **Geographic niche is OK** — region-specific tools (e.g., alerts for a specific country) are acceptable

---

## Format Rules

### Entry format:
```
* [Name](link) – Single sentence description.
```

- Use `–` (em dash, U+2013), not `-` (hyphen)
- One entry per line
- Add new entries at the **bottom** of the relevant section
- No trailing punctuation style inconsistency — match the existing list style

### For open-source entries, optionally link the source:
```
* [Name](https://t.me/botname) – [Open Source](https://github.com/user/repo) Single sentence description.
```

---

## Section Placement

| Entry type | Section |
|---|---|
| Telegram bots | `## Bots` |
| Inline bots | `### Inline Bots` |
| Games | `### Games` |
| Python libraries | `### Bot Libs > #### Python` |
| JS/TS/Node libraries | `### Bot Libs > #### Javascript/Typescript/Node` |
| Other language libraries | appropriate `### Bot Libs` subsection |
| Telegram-specific tools | `## Tools` |
| Multi-platform tools (Telegram + others) | `## Multi-platform Tools` |
| Telegram themes | `## Themes` |
| Telegram groups | `## Groups` |
| Telegram channels | `## Channels` |
| Bot stores/directories | `## Bot Stores` or `## Telegram Directory` |
| Security-focused channels | `## Security` |

---

## PR Review Checklist

When reviewing a PR, check:

1. [ ] Does the entry relate to Telegram?
2. [ ] Is there a valid link?
3. [ ] Is the description a single concise sentence?
4. [ ] Does it use `–` (em dash)?
5. [ ] Is it placed at the bottom of the correct section?
6. [ ] Is the PR title meaningful (not "Update README.md")?
7. [ ] Are there any copyright or safety concerns?
8. [ ] If multi-platform, is it in `## Multi-platform Tools`?

---

## Suggested Comment Templates

### Requesting a shorter description:
> The description is a bit long for this list — each entry should be a single concise sentence.
> Suggested: `* [Name](link) – <one sentence>.`

### Requesting a link:
> Could you add a link to the project page or website?

### Requesting description clarity:
> Could you update the description to explain what the bot/tool actually does in one sentence?

### Closing for copyright:
> This entry raises copyright concerns (e.g., provides unlicensed streaming or download links). We cannot include it.

### Closing for safety:
> Crypto trading bots that request API keys via Telegram raise safety concerns for our users. We cannot include this entry.

