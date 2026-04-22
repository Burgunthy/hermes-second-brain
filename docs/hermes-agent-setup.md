# Hermes Agent Setup Guide

> **Complete guide for integrating Hermes Agent with Second Brain**

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Install Hermes](#step-1-install-hermes)
4. [Step 2: Configure API Provider](#step-2-configure-api-provider)
5. [Step 3: Create config.yaml](#step-3-create-configyaml)
6. [Step 4: Add Project Context](#step-4-add-project-context)
7. [Step 5: Create Skills](#step-5-create-skills)
8. [Step 6: Start Hermes](#step-6-start-hermes)
9. [Discord Integration](#discord-integration)
10. [Cron Automation](#cron-automation)
11. [Operations Guide](#operations-guide)
12. [Troubleshooting](#troubleshooting)

---

## Overview

Hermes is an always-on AI agent that serves as the **Executor** of your Second Brain.

```
┌──────────────┐  ┌──────────┐  ┌──────────────┐
│   Discord    │  │   CLI    │  │ Claude Code  │
│    (you)     │  │ (you)    │  │  (Director)  │
└──────┬───────┘  └────┬─────┘  └──────┬───────┘
       │               │               │
       └───────────────┼───────────────┘
                       ▼
              ┌─────────────────┐
              │  Hermes Agent   │
              │   (Executor)    │
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    Wiki Query    Raw Ingest    Script Exec
```

### Directory Structure

```
~/system/
├── .venv/              # Python virtual environment
├── hermes/             # → symlink to ~/.hermes/ (config, sessions, skills)
└── second-brain/       # Your knowledge base (Obsidian vault)
```

---

## Prerequisites

- **Python 3.10+**
- **python3-venv** — on Ubuntu/Debian: `sudo apt install python3-venv`
- **Git**
- **LLM API key** from a supported provider
- **Discord Bot** (optional, for Discord access)

---

## Step 1: Install Hermes

```bash
# Create virtual environment
python3 -m venv ~/system/.venv
source ~/system/.venv/bin/activate

# Install from GitHub (not on PyPI)
pip install git+https://github.com/NousResearch/hermes-agent.git

# Verify
hermes --version

# Optional: add alias for convenience
echo 'alias hermes="$HOME/system/.venv/bin/hermes"' >> ~/.bashrc
source ~/.bashrc
```

---

## Step 2: Configure API Provider

Hermes needs an LLM provider. Pick one:

| Provider | API Key Format | Base URL | Example Model |
|----------|---------------|----------|---------------|
| **Anthropic** | `sk-ant-...` | `https://api.anthropic.com` | `claude-sonnet-4` |
| **OpenAI** | `sk-...` | `https://api.openai.com/v1` | `gpt-4o` |
| **OpenRouter** | `sk-or-...` | `https://openrouter.ai/api/v1` | `anthropic/claude-sonnet-4` |
| **Ollama (local)** | N/A | `http://localhost:11434/v1` | `llama3` |

---

## Step 3: Create config.yaml

```bash
# Create config directory + symlink
mkdir -p ~/.hermes
ln -sf ~/.hermes ~/system/hermes

# Create .env with your API key
cat > ~/.hermes/.env << 'EOF'
LLM_API_KEY=sk-your-actual-key-here
LLM_BASE_URL=https://api.anthropic.com
EOF
chmod 600 ~/.hermes/.env

# Create config
cat > ~/.hermes/config.yaml << 'EOF'
model:
  default: claude-sonnet-4       # ← change to your model
  providers: {}

terminal:
  backend: local
  cwd: ~/system/second-brain    # ← your knowledge base path
  timeout: 180

agent:
  max_turns: 90
  gateway_timeout: 1800

memory:
  memory_enabled: true
  user_profile_enabled: true
EOF
```

### Config Reference

| Field | Required | Description |
|-------|----------|-------------|
| `model.default` | ✅ | Model name for your provider |
| `model.providers` | No | Provider-specific overrides |
| `terminal.cwd` | ✅ | Where Hermes works (your vault) |
| `terminal.timeout` | No | Shell command timeout in seconds |

---

## Step 4: Add Project Context

Hermes reads `.hermes.md` from the `terminal.cwd` directory. This file tells Hermes its role and rules.

> ⚠️ The `.hermes.md` below contains a nested code block (the frontmatter example). Bash heredoc cannot handle this — use the Python command instead:

```bash
python3 << 'PYEOF'
content = """# Second Brain — Hermes Context

## Purpose
You are the Executor of this knowledge base. Your job:
1. **Query**: Search wiki/ for evidence-based answers
2. **Ingest**: Transform raw/ files into structured wiki/ entries
3. **Maintain**: Fix broken links, remove duplicates, check consistency
4. **Automate**: Execute scheduled tasks (daily ingest, weekly lint)

## Directory Map
- `raw/` — Original source materials (NEVER modify these)
- `raw/inbox/` — Incoming unclassified files
- `wiki/concepts/` — Concept definitions
- `wiki/entities/` — People, companies, tools
- `wiki/sources/` — Source summaries
- `wiki/synthesis/` — Cross-cutting analysis
- `wiki/log.md` — Change log (update on every wiki edit)
- `wiki/index.md` — Master index

## Ingest Process
For each file in raw/:
1. Read the file content
2. Extract key concepts → create/update `wiki/concepts/<name>.md`
3. Extract entities (people, tools, companies) → `wiki/entities/`
4. Write a source summary → `wiki/sources/<name>.md`
5. Add [[wikilinks]] between related documents
6. Update `wiki/log.md` with what changed
7. Update `wiki/index.md` if new categories were added

## Rules
- Never modify files in raw/
- Always add YAML frontmatter to wiki files
- Always cite sources with [[wikilink]] syntax
- Answer "I don't know" when uncertain — never fabricate
- Keep wiki/log.md updated

## Frontmatter Schema
```yaml
title: Document Title
type: concept | entity | source_summary | synthesis
related: [[OtherDoc1]] [[OtherDoc2]]
sources: raw/path/to/original.md
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
```
"""
with open("$HOME/system/second-brain/.hermes.md", "w") as f:
    f.write(content)
print("Created .hermes.md")
PYEOF
```

---

## Step 5: Create Skills

Skills are reusable instructions stored as Markdown files. Hermes looks for skills in `~/.hermes/skills/` (accessible via `~/system/hermes/skills/`).

### Wiki Query Skill

```bash
mkdir -p ~/.hermes/skills/wiki-query
cat > ~/.hermes/skills/wiki-query/SKILL.md << 'EOF'
---
name: wiki-query
description: Search Second Brain wiki and answer questions
---

# Wiki Query

## Steps
1. Extract keywords from the user's question
2. Search `wiki/concepts/` and `wiki/entities/` for matches
3. Follow [[wikilinks]] to find related documents
4. Synthesize findings into a structured answer

## Output Format
- Start with a direct answer
- List evidence: `- [[SourceDoc]]: brief summary`
- Note any gaps in knowledge
EOF
```

### Wiki Ingest Skill

```bash
mkdir -p ~/.hermes/skills/wiki-ingest
cat > ~/.hermes/skills/wiki-ingest/SKILL.md << 'EOF'
---
name: wiki-ingest
description: Ingest a raw file into the wiki
---

# Wiki Ingest

## Steps
1. Read the target file from raw/
2. Determine type (concept, entity, or source)
3. Extract key information
4. Create wiki file with proper frontmatter
5. Add [[wikilinks]] to existing related documents
6. Update wiki/log.md
7. Update wiki/index.md if needed

## File Placement
- New concepts → `wiki/concepts/<slug>.md`
- New entities → `wiki/entities/<type>/<slug>.md`
- Source summaries → `wiki/sources/<slug>.md`
EOF
```

### Wiki Lint Skill

```bash
mkdir -p ~/.hermes/skills/wiki-lint
cat > ~/.hermes/skills/wiki-lint/SKILL.md << 'EOF'
---
name: wiki-lint
description: Check wiki consistency and fix issues
---

# Wiki Lint

## Checks
1. Broken [[wikilinks]] — target file doesn't exist
2. Missing frontmatter — files without YAML header
3. Stale `updated:` dates — not matching recent edits
4. Orphan files — wiki pages with no incoming links
5. Duplicate concepts — same topic covered in multiple files

## Fixes
- Remove links to non-existent files
- Add minimal frontmatter where missing
- Report orphans for manual review
- Merge duplicates when content overlaps
EOF
```

---

## Step 6: Start Hermes

### CLI Mode (one-shot queries)

```bash
# Activate venv
source ~/system/.venv/bin/activate

# Single question
hermes chat -q "What is in raw/inbox?"

# Interactive session
hermes chat
```

### Daemon Mode (always-on)

```bash
# Run gateway in foreground (recommended)
~/system/.venv/bin/hermes gateway run

# Or start as systemd service
~/system/.venv/bin/hermes gateway install
~/system/.venv/bin/hermes gateway start

# Check status
~/system/.venv/bin/hermes gateway status
```

### Systemd (Linux, for auto-start)

Hermes has a built-in systemd installer — use `hermes gateway install` (above).

Or create manually:

```bash
cat > ~/.config/systemd/user/hermes-gateway.service << 'EOF'
[Unit]
Description=Hermes Gateway
After=network.target

[Service]
Type=simple
ExecStart=/home/YOURUSER/system/.venv/bin/hermes gateway run
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable hermes-gateway
systemctl --user start hermes-gateway
```

> ⚠️ Replace `YOURUSER` with your actual username.

---

## Discord Integration

### Create a Discord Bot

1. Go to **[Discord Developer Portal](https://discord.com/developers/applications)**
2. Click **"New Application"** → name it (e.g., "Second Brain Bot")
3. Go to **"Bot"** tab → click **"Reset Token"** → **copy the token**
4. Enable **Privileged Gateway Intents**:
   - ✅ **Message Content Intent** (required)
   - ✅ **Server Members Intent** (optional)
5. Go to **"OAuth2"** → **"URL Generator"**:
   - Scopes: `bot`
   - Permissions: Send Messages, Read Messages, Add Reactions, Attach Files, Embed Links
   - Copy the URL and invite the bot to your server

### Configure Discord

```bash
# Add to ~/.hermes/.env
cat >> ~/.hermes/.env << 'EOF'
DISCORD_BOT_TOKEN=your-bot-token-here
DISCORD_ALLOWED_USERS=your-discord-user-id
EOF
chmod 600 ~/.hermes/.env
```

Add Discord section to `~/.hermes/config.yaml`:

```yaml
discord:
  require_mention: true
  allowed_channels: ""
  auto_thread: true
  reactions: true
```

---

## Cron Automation

### Ingest Script

> The ingest script is defined in [Second Brain Setup → Ingest Pipeline](./second-brain-setup.md#ingest-pipeline). If you haven't set it up yet, follow that guide first.

### Set Up Cron

```bash
crontab -e

# Add these lines:
# Daily 4am: ingest
0 4 * * * $HOME/system/.venv/bin/hermes chat -q "Ingest everything in raw/inbox/"

# Weekly Sunday 3am: wiki lint
0 3 * * 0 $HOME/system/.venv/bin/hermes chat -q "Run wiki-lint on the entire wiki/ directory."
```

---

## Operations Guide

### Daily

```bash
source ~/system/.venv/bin/activate
hermes chat -q "What's in raw/inbox?"
hermes chat -q "Ingest everything in raw/inbox/"
```

### Weekly

```bash
hermes chat -s wiki-lint -q "Full wiki consistency check"
```

### Useful Paths

| What | Path |
|------|------|
| Activate venv | `source ~/system/.venv/bin/activate` |
| Config | `~/.hermes/config.yaml` or `~/system/hermes/config.yaml` |
| API keys | `~/.hermes/.env` |
| Skills | `~/.hermes/skills/` or `~/system/hermes/skills/` |
| Knowledge base | `~/system/second-brain/` |
| Gateway log | `~/system/hermes/logs/` |

---

## Troubleshooting

### `hermes` command not found
```bash
source ~/system/.venv/bin/activate
# Or use full path: ~/system/.venv/bin/hermes
```

### API key errors
```bash
cat ~/.hermes/.env
# Make sure LLM_API_KEY has your actual key
```

### Hermes not responding in Discord
1. Check the bot is online in your Discord server
2. Verify `DISCORD_BOT_TOKEN` in `~/.hermes/.env`
3. Verify Message Content Intent is enabled in Developer Portal
4. Check logs: `~/system/.venv/bin/hermes logs`

---

## Setup Checklist

- [ ] Python 3.10+ installed
- [ ] `~/system/.venv/` created with Hermes installed
- [ ] `~/.hermes/.env` has real API key
- [ ] `~/.hermes/config.yaml` has correct model + `cwd: ~/system/second-brain`
- [ ] `~/system/hermes` symlink exists → `~/.hermes/`
- [ ] `~/system/second-brain/` directory structure created
- [ ] `~/system/second-brain/.hermes.md` project context added
- [ ] Skills created (wiki-query, wiki-ingest, wiki-lint)
- [ ] `hermes chat -q "Hello"` works
- [ ] (Optional) Discord bot configured
- [ ] (Optional) Cron jobs set up

---

**Version**: 4.0.0 | **Last Updated**: 2026-04-22
