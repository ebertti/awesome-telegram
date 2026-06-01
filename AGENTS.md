# AGENTS.md — PR Review Rules for AI Agents

This file defines the rules that AI agents (automated reviewers, bots, Claude, etc.) should follow when evaluating pull requests to this repository.

---

## What this repository is

A curated list of Telegram-related resources: bots, tools, libraries, channels, groups, and integrations.

**The core criterion is: does this have a meaningful relation to Telegram?**
Multi-platform tools are welcome. Closed-source projects are welcome. The entry just needs to be useful to someone in the Telegram ecosystem.

---

## Acceptance Rules

### ✅ ACCEPT (or approve after minor fixes) if:

- Entry is related to Telegram (can also support other platforms)
- Has a valid link (t.me, GitHub, website, etc.)
- Description is a single concise sentence
- Uses em dash `–` (not hyphen `-`)
- Added at the bottom of the correct section
- PR title is descriptive (not "Update README.md")

### ⚠️ REQUEST CHANGES if:

| Issue | What to ask |
|---|---|
| Description is missing or vague | Ask for a one-sentence description of what it does |
| Description is too long / marketing-heavy | Suggest a trimmed single-sentence version |
| Uses `-` instead of `–` | Ask to replace with em dash |
| No link provided | Ask for project page, t.me, or website |
| Bot handle does not match branding | Ask to clarify / reconcile |
| Wrong section placement | Point to the correct section |
| Multi-platform tool placed in `## Tools` | Ask to move to `## Multi-platform Tools` |

### ❌ CLOSE/REJECT if:

| Reason | Example |
|---|---|
| Copyright-infringing content | Bot providing unlicensed streaming/download links |
| Crypto trading bot requesting API keys | High risk of scam/phishing for users |
| Self-promotion of paid/adult gated content | Private VIP content groups |
| PR title is "Update README.md" AND content is low quality | Violates contributing guidelines |

---

## Format Reference

```
* [Name](https://link.to/project) – One sentence description.
```

With open-source link:
```
* [Name](https://t.me/botname) – [Open Source](https://github.com/user/repo) One sentence description.
```

---

## Section Reference

| What | Where |
|---|---|
| Bots | `## Bots` |
| Inline bots | `### Inline Bots` |
| Games | `### Games` |
| Bot libraries (by language) | `### Bot Libs > #### <Language>` |
| Telegram-specific tools | `## Tools` |
| Multi-platform tools with Telegram support | `## Multi-platform Tools` |
| Themes | `## Themes` |
| Groups | `## Groups` |
| Channels | `## Channels` |
| Bot stores / directories | `## Bot Stores` / `## Telegram Directory` |
| Security channels | `## Security` |

---

## Important Notes

- **Source code is NOT required.** Closed-source bots, tools, and services are accepted.
- **Multi-platform is OK.** If Telegram is one of several supported platforms, place the entry in `## Multi-platform Tools`.
- **Niche/regional tools are OK.** Location-specific tools (e.g., alerts for a specific country) are accepted.
- **One PR = one entry.** Each PR should add a single entry to the list.
- **New entries go at the bottom of their section.**

