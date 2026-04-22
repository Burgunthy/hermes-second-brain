# Quick Start Guide

> **Get your Second Brain running in 10 minutes**

---

## ⚠️ Before You Start

You'll need:
- **Python 3.10+** — check with `python3 --version`
- **python3-venv** — on Ubuntu/Debian: `sudo apt install python3-venv`
- **Git** — check with `git --version`
- **An LLM API key** — Anthropic, OpenAI, or any OpenAI-compatible provider

---

## The Directory Structure

After setup, your `~/system/` will look like:

```
~/system/
├── .venv/              # Hermes virtual environment
├── hermes/             # → symlink to ~/.hermes/ (config, sessions, skills)
└── second-brain/       # Your knowledge base (Obsidian vault)
```

---

## Minutes 1–2: Create the Knowledge Base

```bash
# Create all directories at once
mkdir -p ~/system/second-brain/{raw/{inbox,articles,papers,notes,meetings,videos,code,research,stock},wiki/{concepts,entities/{persons,companies,tools},sources,synthesis},output,scripts/{inbox-watcher/lib,inbox-watcher/logs,logs}}

# Initialize Git
cd ~/system/second-brain
git init
git config user.email "you@example.com"
git config user.name "Your Name"

# Create .gitignore
cat > .gitignore << 'EOF'
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
EOF

git add .
git commit -m "Initial commit: Second Brain structure"
```

---

## Minutes 3–4: Obsidian Setup

1. Install Obsidian: https://obsidian.md
2. Open `~/system/second-brain` as a Vault
3. Go to **Settings → Community Plugins** → enable community plugins
4. Install **Dataview** plugin (required for the wiki index to work)

---

## Minutes 5–6: Create Base Documents

```bash
cd ~/system/second-brain

# Wiki Log
cat > wiki/log.md << 'EOF'
---
title: Wiki Change Log
type: log
---

# Wiki Change Log
EOF

# Wiki Index (use python to avoid backtick escaping issues with heredoc)
python3 -c "
content = '''---
title: Wiki Index
type: index
---

# Wiki Index

## Concepts

\`\`\`dataview
LIST
FROM \"wiki/concepts\"
\`\`\`

## Entities

\`\`\`dataview
LIST
FROM \"wiki/entities\"
\`\`\`
'''
with open('wiki/index.md', 'w') as f:
    f.write(content)
"

# Test file in inbox
cat > raw/inbox/test.md << 'EOF'
# Test Note

This is my first note in the Second Brain system.
EOF
```

---

## Minutes 7–10: Install Hermes Agent

### Step 1: Create Virtual Environment

```bash
# Create venv inside ~/system/
python3 -m venv ~/system/.venv
source ~/system/.venv/bin/activate
```

### Step 2: Install Hermes from GitHub

Hermes is not on PyPI — install directly from GitHub:

```bash
pip install git+https://github.com/NousResearch/hermes-agent.git

# Verify
hermes --version
```

### Step 3: Configure

```bash
# Create config directory (Hermes creates ~/.hermes/ on first run)
mkdir -p ~/.hermes

# Create symlink inside ~/system/ for easy access
ln -sf ~/.hermes ~/system/hermes

# Create config.yaml
cat > ~/.hermes/config.yaml << 'EOF'
model:
  default: YOUR_MODEL_NAME    # e.g., claude-sonnet-4, gpt-4o, glm-5.1
  providers: {}

terminal:
  backend: local
  cwd: ~/system/second-brain  # Points to your knowledge base
  timeout: 180

agent:
  max_turns: 90
  gateway_timeout: 1800

memory:
  memory_enabled: true
  user_profile_enabled: true
EOF

# Create .env with your API key
cat > ~/.hermes/.env << 'EOF'
# Replace with your actual API key and endpoint
LLM_API_KEY=sk-your-actual-api-key-here
LLM_BASE_URL=https://api.anthropic.com
EOF
chmod 600 ~/.hermes/.env
```

### Step 4: Add Project Context

```bash
cat > ~/system/second-brain/.hermes.md << 'EOF'
# Second Brain — Hermes Context

## Purpose
You are the Executor of this knowledge base. Your job:
1. **Query**: Search wiki/ for evidence-based answers
2. **Ingest**: Transform raw/ files into structured wiki/ entries
3. **Maintain**: Fix broken links, remove duplicates, check consistency
4. **Automate**: Execute scheduled tasks (daily ingest, weekly lint)

## Rules
- Never modify raw/ folder
- Log all wiki/ changes to wiki/log.md
- Cite sources using [[wikilink]] format
EOF
```

### Step 5: Test

```bash
source ~/system/.venv/bin/activate
hermes chat -q "Hello! List what's in raw/inbox/"
```

✅ **Done!** Your Second Brain is ready.

---

## What's Where

| Path | Purpose |
|------|---------|
| `~/system/.venv/` | Python virtual environment with Hermes |
| `~/system/hermes/` | Symlink → `~/.hermes/` (config, skills, sessions) |
| `~/system/second-brain/` | Your knowledge base (Obsidian vault) |
| `~/.hermes/config.yaml` | Hermes configuration |
| `~/.hermes/.env` | API keys (keep secret!) |

---

## Next Steps

- 📖 [**Second Brain Setup**](./second-brain-setup.md) — Full system guide with Inbox Watcher, Obsidian templates, automation scripts
- 🤖 [**Hermes Agent Setup**](./hermes-agent-setup.md) — Skills, Discord integration, cron automation
