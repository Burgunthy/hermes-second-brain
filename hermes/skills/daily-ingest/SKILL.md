---
name: daily-ingest
description: Force execute the daily ingest flow (watcher + ingest)
tags: discord, ingest, wiki, automation
---

# Daily Ingest Skill

Discord `/daily-ingest` command to force execute the daily ingest flow.

## Manual Execution (from Hermes session)

### Step 1: Scan inbox
```bash
ls ~/system/second-brain/raw/inbox/
```

### Step 2: Parallel ingest via delegate_task
For multiple files, use `delegate_task(tasks=[...])` with up to 3 parallel tasks.
Each task context should include:
- Read wiki/ files and check existing documents before creating/updating
- Frontmatter: title, type, related, sources, created, updated
- Valid types: `concept`, `entity`, `source_summary`, `synthesis`
- Wikilink format: `[[Title]]`
- Must update wiki/index.md and wiki/log.md

### Step 3: Graph update + lint
```bash
python3 ~/system/scripts/wiki-graph.py
python3 ~/system/scripts/wiki-lint.py
```

## Pitfalls
- Use `source_summary` not `source` (lint catches `invalid_type`)
- Korean title + English filename is normal
- Avoid writing `[[wikilinks]]` inside code blocks (false broken_link detection)
