---
name: daily-ingest
description: Force execute the daily ingest flow (watcher + ingest)
tags: discord, ingest, wiki, automation
---

# Daily Ingest Skill

Discord `/daily-ingest` command to force execute the daily ingest flow.

## How It Works

1. Discord receives `/daily-ingest` command
2. Hermes scans `raw/inbox/` for unprocessed files
3. Each file is read, concepts/entities extracted
4. Files are ingested into `wiki/concepts/` or `wiki/entities/`
5. `wiki/index.md` and `wiki/log.md` are updated
6. Knowledge graph is regenerated via `wiki-graph.py`
7. Results reported to Discord

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
- **Sub-agent type error**: Use `source_summary` not `source` (lint catches `invalid_type`)
- **Korean title + English filename**: Normal. Lint reports as info level
- **index.md/log.md race condition**: Parallel sub-agents may conflict. Patch sequentially
- **Code block wikilinks**: `[[example]]` inside backticks causes false broken_link detection. Avoid writing wikilinks in code blocks
