# Hermes Second Brain

> A compound knowledge system — Obsidian vault + knowledge graph + Hermes Agent automation.

Clone this repo to `~/system/` and any LLM can reconstruct the same setup from the README alone.

---

## Structure

```
hermes-second-brain/
├── README.md                          # This file
├── second-brain/                      # → ~/system/second-brain/ (Obsidian vault)
│   ├── CLAUDE.md                      # Claude Code guide
│   ├── .hermes.md                     # Hermes project context
│   ├── raw/                           # Raw materials (never modify)
│   │   ├── inbox/                     # Unprocessed items
│   │   ├── articles/                  # Web articles
│   │   ├── papers/                    # Research papers
│   │   └── notes/                     # Manual notes
│   ├── wiki/                          # Curated knowledge base
│   │   ├── index.md                   # Master index
│   │   ├── log.md                     # Change log
│   │   ├── concepts/                  # Concept documents
│   │   ├── entities/                  # Entity documents (tools, people, products)
│   │   ├── sources/                   # Source summaries
│   │   └── synthesis/                 # Synthesis / analysis
│   ├── graphify-out/                  # Knowledge graph output
│   └── output/                        # Generated reports
├── scripts/
│   ├── wiki-graph.py                  # Wiki → knowledge graph generator
│   └── wiki-lint.py                   # Wiki consistency checker
├── hermes/skills/                     # Hermes Agent skills
│   ├── daily-ingest/
│   ├── archive/
│   └── research/
└── kor/README.md                      # Korean translation
```

---

## Architecture

Four components forming a compound knowledge system:

| Component | Role | Location |
|-----------|------|----------|
| **Obsidian** | Knowledge base (vault) | `~/system/second-brain/` |
| **Graphify** | Wikilinks → knowledge graph | `~/system/scripts/wiki-graph.py` |
| **Claude Code** | Director — complex ingest, system design | Local terminal |
| **Hermes Agent** | Executor — collection, ingest, cron automation | Server (Discord/CLI) |

**Key principle**: Claude Code delegates, Hermes executes. Claude Code never touches files directly.

```
Claude Code (Director)          Hermes Agent (Executor)
      │                                │
      │── "ingest this to wiki" ──────→ wiki/ CRUD, search, cron
      │←── report ─────────────────────│
      └── feedback ──→ revise ────────→ apply
```

---

## Prerequisites

- **Ubuntu 22.04+** (Linux)
- **Python 3.10+**
- **Node.js 20+** (for Playwright MCP)
- **Claude Code** — `npm install -g @anthropic-ai/claude-code`
- **Git**, **pip + venv** — `sudo apt install git python3-pip python3-venv`

---

## Setup

### 1. Clone

```bash
git clone https://github.com/Burgunthy/hermes-second-brain.git ~/system
```

### 2. Obsidian Vault

Open Obsidian → "Open folder as vault" → select `~/system/second-brain/`.

### 3. Knowledge Graph

```bash
python3 ~/system/scripts/wiki-graph.py
# → generates graphify-out/graph.json, graph.html, stats.json
```

### 4. Claude Code

`second-brain/CLAUDE.md` instructs Claude Code to delegate to Hermes instead of editing files directly:

```bash
cd ~/system/second-brain
claude
```

### 5. Hermes Agent

```bash
python3 -m venv ~/system/.venv
source ~/system/.venv/bin/activate
pip install git+https://github.com/NousResearch/hermes-agent.git
pip install playwright
npx playwright install chromium
```

### 6. Hermes Config

Edit `~/.hermes/config.yaml`:
- `model.default` → your preferred model
- `terminal.cwd` → `~/system/second-brain`

Set API keys:

```bash
export DISCORD_BOT_TOKEN="***"
export OPENAI_API_KEY="***"
```

### 7. systemd Service (always-on)

```bash
# Create ~/.config/systemd/user/hermes-gateway.service, then:
systemctl --user daemon-reload
systemctl --user enable hermes-gateway
systemctl --user start hermes-gateway
```

### 8. Skills

```bash
cp -r ~/system/hermes/skills/* ~/.hermes/skills/
```

---

## Automation

### Daily Ingest (4:00 AM)

```bash
hermes chat -q "create cronjob: daily-ingest, 0 4 * * *, ingest raw/inbox/ to wiki/ and refresh graph, deliver: discord"
```

### Weekly Lint / Summary

```bash
hermes chat -q "create cronjob: weekly-lint, 0 5 * * 0, run wiki-lint.py and report"
hermes chat -q "create cronjob: weekly-summary, 0 9 * * 1, summarize last week's wiki changes"
```

---

## Ingest Pipeline

```
raw/ file → extract concepts/entities → wiki/concepts/ or wiki/entities/
         → create wiki/sources/ summary
         → update wiki/index.md
         → log to wiki/log.md
```

### Document Metadata

```yaml
---
title: Document title
type: concept | entity | source_summary | synthesis
related: "[[RelatedDoc1]] [[RelatedDoc2]]"
sources: raw/file-path.md
created: 2026-04-22
updated: 2026-04-22
---
```

### Rules

- **raw/**: Never modify (preserve originals)
- **wiki/**: Log all changes in `wiki/log.md`
- **wiki/index.md**: Keep up to date

---

## License

MIT

---

[한국어 README](kor/README.md)
