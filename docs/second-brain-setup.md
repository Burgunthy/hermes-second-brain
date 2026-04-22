# Second Brain Setup Guide

> **Full guide for the Second Brain knowledge management system**

---

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Setting Up Obsidian](#setting-up-obsidian)
4. [Inbox Watcher](#inbox-watcher)
5. [Ingest Pipeline](#ingest-pipeline)
6. [Git Workflow](#git-workflow)
7. [Templates](#templates)

---

## Overview

The Second Brain is a structured knowledge base powered by Obsidian and automated by Hermes Agent.

```
Files arrive → raw/inbox/
                    ↓
          Inbox Watcher classifies
                    ↓
     raw/articles/ | raw/papers/ | raw/notes/ | ...
                    ↓
          Hermes ingests into wiki/
                    ↓
     wiki/concepts/ | wiki/entities/ | wiki/sources/
```

### Directory Structure

```
~/system/second-brain/
├── .hermes.md                    # Hermes project context
├── .gitignore
├── raw/                          # Original materials (NEVER modify)
│   ├── inbox/                    # Unclassified incoming files
│   ├── articles/                 # Web articles and blog posts
│   ├── papers/                   # Academic papers
│   ├── notes/                    # Manual notes and memos
│   ├── meetings/                 # Meeting notes
│   ├── videos/                   # Video transcripts
│   ├── code/                     # Code snippets and projects
│   ├── research/                 # Research notes
│   └── stock/                    # Stock/investment notes
├── wiki/                         # Refined knowledge base
│   ├── index.md                  # Master index (Dataview-powered)
│   ├── log.md                    # Change log
│   ├── concepts/                 # Concept definitions
│   ├── entities/                 # Structured entity pages
│   │   ├── persons/
│   │   ├── companies/
│   │   └── tools/
│   ├── sources/                  # Source summaries
│   └── synthesis/                # Cross-cutting analysis
├── output/                       # Generated reports and exports
├── graphify-out/                 # Knowledge graph output
└── scripts/                      # Automation scripts
    ├── hermes-ingest.sh
    ├── daily-ingest-flow.sh
    ├── inbox-watcher/
    │   ├── sort-all.sh
    │   ├── lib/
    │   └── logs/
    └── logs/
```

---

## Setting Up Obsidian

### Install

1. Download from https://obsidian.md
2. Open `~/system/second-brain` as a vault

### Required Plugins

| Plugin | Purpose |
|--------|---------|
| **Dataview** | Dynamic queries in wiki/index.md |
| **Graph Analysis** (optional) | Visualize wiki graph |

### Recommended Settings

- **Editor**: Source mode for `.md` files
- **Files & Links**: Use `[[wikilink]]` format
- **Appearance**: Dark theme recommended

---

## Inbox Watcher

The Inbox Watcher automatically classifies files from `raw/inbox/` into appropriate subdirectories.

### Setup

```bash
# Create the watcher script
cat > ~/system/second-brain/scripts/inbox-watcher/sort-all.sh << 'SCRIPT'
#!/bin/bash
# sort-all.sh — Classify all files in raw/inbox/
INBOX="$HOME/system/second-brain/raw/inbox"
LOG="$HOME/system/second-brain/scripts/inbox-watcher/logs"

mkdir -p "$LOG"

classify() {
    local file="$1"
    local name=$(basename "$file")
    local target="notes"  # default

    case "$name" in
        *paper*|*논문*|*arxiv*)  target="papers" ;;
        *article*|*기사*|*블로그*) target="articles" ;;
        *meeting*|*회의*|*미팅*) target="meetings" ;;
        *video*|*영상*|*유튜브*) target="videos" ;;
        *code*|*코드*|*프로그래밍*) target="code" ;;
        *research*|*연구*|*조사*) target="research" ;;
        *stock*|*주식*|*투자*)    target="stock" ;;
    esac

    local dest="$HOME/system/second-brain/raw/$target"
    mkdir -p "$dest"
    mv "$file" "$dest/"
    echo "[$(date '+%Y-%m-%d %H:%M')] $name → $target" >> "$LOG/classify.log"
}

# Process all .md files in inbox
find "$INBOX" -maxdepth 1 -name "*.md" -type f | while read -r file; do
    classify "$file"
done
SCRIPT
chmod +x ~/system/second-brain/scripts/inbox-watcher/sort-all.sh
```

### Run Manually

```bash
~/system/second-brain/scripts/inbox-watcher/sort-all.sh
```

---

## Ingest Pipeline

### Manual Ingest

```bash
source ~/system/.venv/bin/activate
hermes chat -q "Ingest raw/inbox/topic.md into wiki/"
```

### Batch Ingest

```bash
~/system/second-brain/scripts/hermes-ingest.sh --all
```

### Full Daily Flow

1. Inbox Watcher classifies new files
2. Hermes ingests classified files into wiki/
3. Wiki log and index are updated

```bash
# Classify
~/system/second-brain/scripts/inbox-watcher/sort-all.sh

# Ingest
~/system/second-brain/scripts/hermes-ingest.sh --all
```

---

## Git Workflow

```bash
cd ~/system/second-brain

# Check status
git status

# Stage and commit changes
git add -A
git commit -m "Ingest: added 3 new wiki entries"

# Push to remote (optional)
git remote add origin git@github.com:YOURUSER/second-brain.git
git push -u origin main
```

### .gitignore

```gitignore
.obsidian/
*.tmp
*.log
.DS_Store
graphify-out/
output/
graph.json
graph.html
.env
.local.*
.pipeline/
pipeline.db
```

---

## Templates

### Wiki Concept Template

```markdown
---
title: Concept Name
type: concept
related: [[RelatedConcept1]] [[RelatedConcept2]]
sources: raw/path/to/original.md
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
---

# Concept Name

## Definition
...

## Key Points
- Point 1
- Point 2

## Related
- [[RelatedConcept1]] — brief relationship
```

### Wiki Entity Template

```markdown
---
title: Entity Name
type: entity
subtype: person | company | tool
related: [[RelatedEntity1]]
sources: raw/path/to/original.md
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
---

# Entity Name

## Overview
...

## Details
...
```

### Source Summary Template

```markdown
---
title: Source Title
type: source_summary
related: [[Concept1]] [[Concept2]]
sources: raw/path/to/original.md
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
---

# Source Summary: Source Title

## TL;DR
...

## Key Insights
1. ...
2. ...

## Quotes
> "Notable quote from the source"
```

---

**Version**: 4.0.0 | **Last Updated**: 2026-04-22
