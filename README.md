<div align="center">

# 🧠 Hermes Second Brain

**A compound knowledge system that grows itself.**

*Obsidian vault · Knowledge graph · Hermes Agent automation*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](scripts/)
[![Node.js 20+](https://img.shields.io/badge/Node.js-20+-339933.svg)]()

</div>

---

## ✨ What is this?

A self-growing second brain built on four components:

| | Component | Role |
|---|-----------|------|
| 📝 | **Obsidian** | Markdown knowledge base (vault) |
| 🔗 | **Graphify** | Wikilinks → interactive knowledge graph |
| 🧑‍💻 | **Claude Code** | Director — orchestrates complex tasks |
| 🤖 | **Hermes Agent** | Executor — collects, ingests, automates via cron |

> **Key idea**: Claude Code *delegates*, Hermes *executes*. The system runs 24/7 on a server — accessible from Discord or CLI.

---

## 📂 Structure

Clone to `~/system/` and the directory *is* the system. No extra config needed.

```
hermes-second-brain/
├── second-brain/                 # Obsidian vault
│   ├── CLAUDE.md                 # Claude Code instructions
│   ├── .hermes.md                # Hermes project context
│   ├── raw/                      # Raw materials (never modify)
│   │   ├── inbox/                #   Unprocessed items
│   │   ├── articles/             #   Web articles
│   │   ├── papers/               #   Research papers
│   │   └── notes/                #   Manual notes
│   ├── wiki/                     # Curated knowledge base
│   │   ├── concepts/             #   Concept documents
│   │   ├── entities/             #   Entity documents
│   │   ├── sources/              #   Source summaries
│   │   └── synthesis/            # Integrated analysis
│   └── graphify-out/             # Knowledge graph output
├── scripts/
│   ├── wiki-graph.py             # Wiki → graph generator
│   └── wiki-lint.py              # Consistency checker
├── hermes/skills/                # Hermes Agent skills
└── kor/README.md                 # 한국어 버전
```

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/Burgunthy/hermes-second-brain.git ~/system

# 2. Knowledge graph
python3 ~/system/scripts/wiki-graph.py

# 3. Hermes Agent
python3 -m venv ~/system/.venv && source ~/system/.venv/bin/activate
pip install git+https://github.com/NousResearch/hermes-agent.git playwright
npx playwright install chromium

# 4. Copy skills
cp -r ~/system/hermes/skills/* ~/.hermes/skills/
```

Open `~/system/second-brain/` as an Obsidian vault and you're set.

<details>
<summary>🔧 Full setup (systemd service, Claude Code, env vars)</summary>

### Claude Code

`second-brain/CLAUDE.md` tells Claude Code to delegate to Hermes:

```bash
cd ~/system/second-brain
claude
```

### Hermes Config

Edit `~/.hermes/config.yaml`:
- `model.default` → your preferred model
- `terminal.cwd` → `~/system/second-brain`

```bash
export DISCORD_BOT_TOKEN="***"
export OPENAI_API_KEY="***"
```

### systemd (always-on)

```bash
# Create ~/.config/systemd/user/hermes-gateway.service, then:
systemctl --user daemon-reload
systemctl --user enable --now hermes-gateway
```

</details>

---

## 🔄 How It Works

```
  Collect                Ingest                Query
┌──────────┐       ┌──────────────┐       ┌──────────┐
│ Articles  │──┐    │  Extract     │       │          │
│ Papers    │  ├────▶  concepts   ├──────▶│  Wiki    │
│ Notes     │──┘    │  entities   │       │  Search  │
└──────────┘       └──────┬───────┘       └──────────┘
                          │
                   ┌──────▼───────┐
                   │ Knowledge   │
                   │ Graph       │
                   └──────────────┘
```

**Ingest pipeline**: `raw/` → extract concepts & entities → `wiki/` → update index & log → refresh graph.

### Document Metadata

Every wiki document uses this frontmatter:

```yaml
---
title: Document Title
type: concept | entity | source_summary | synthesis
related: "[[RelatedDoc1]] [[RelatedDoc2]]"
sources: raw/file-path.md
created: 2026-04-22
updated: 2026-04-22
---
```

---

## ⏰ Automation

Cron jobs run automatically via Hermes Agent:

| Schedule | Job | Description |
|----------|-----|-------------|
| Daily 4 AM | `daily-ingest` | Scan `raw/inbox/` → ingest to wiki → refresh graph |
| Sun 5 AM | `weekly-lint` | Run `wiki-lint.py` consistency checks |
| Mon 9 AM | `weekly-summary` | Summarize last week's wiki changes |

```bash
hermes chat -q "create cronjob: daily-ingest, 0 4 * * *, ingest raw/inbox/ to wiki/ and refresh graph, deliver: discord"
```

---

## 📜 Rules

- **`raw/`** — never modify (preserve originals)
- **`wiki/`** — log all changes in `wiki/log.md`
- **`wiki/index.md`** — always keep up to date

---

## 📄 License

[MIT](LICENSE)

---

<div align="center">

[한국어 README](kor/README.md) · Built with [Hermes Agent](https://github.com/NousResearch/hermes-agent)

</div>
