# Contributing

Thanks for wanting to add something to this list! A few rules to keep it useful and merge-conflict-free.

## Entry format

```
* [Name](https://url) – Single sentence description.
```

- Use `–` (en dash, U+2013), not `-` (hyphen) or `—` (em dash)
- End the description with a period
- One entry, one sentence, one PR

## Alphabetical order — this is the important one

Insert your entry in **alphabetical order** within its section, case-insensitive, ignoring a leading `@` or `[`.

Do **not** just append it at the bottom of the section. Alphabetical order is what keeps the list scannable and, more importantly, is what avoids merge conflicts when several PRs touch the same section at once — an out-of-order entry is the single most common reason a PR gets sent back for changes.

## Sections

Bots → `## Bots` · Inline bots → `### Inline Bots` · Games → `### Games` · Language libraries → `### Bot Libs` (pick the right subsection, e.g. `#### Python`) · Telegram-specific tools → `## Tools` · Tools that also support other platforms → `## Multi-platform Tools` · Themes → `## Themes` · Groups → `## Groups` · Channels → `## Channels` · Directories/stores → `## Bot Stores` or `## Telegram Directory`.

## Not accepted

- Adult/explicit content, gambling/betting bots
- Spam, scam, or self-promotion without clear public value
- Copyright-infringing content (e.g. unlicensed streaming/download links)
- Crypto trading bots that ask for API keys via Telegram
- Broken or inaccessible links

Closed-source entries are fine as long as the description is clear about what the tool does.
