# Second Brain with Hermes Agent

> **Build a self-improving knowledge base that runs itself.**

An always-on AI knowledge management system combining:
- **Obsidian** — structured knowledge base with wiki-style linking
- **Hermes Agent** — AI that ingests, queries, and maintains your knowledge
- **Cron Automation** — daily ingest, weekly lint, hands-off operation

---

## Quick Start

```bash
# 1. Create knowledge base
mkdir -p ~/system/second-brain/{raw/{inbox,articles,papers,notes},wiki/{concepts,entities,sources,synthesis}}
cd ~/system/second-brain && git init

# 2. Install Hermes
python3 -m venv ~/system/.venv
source ~/system/.venv/bin/activate
pip install git+https://github.com/NousResearch/hermes-agent.git

# 3. Configure
mkdir -p ~/.hermes && ln -sf ~/.hermes ~/system/hermes
cat > ~/.hermes/config.yaml << 'EOF'
model:
  default: YOUR_MODEL_NAME
  providers: {}
terminal:
  backend: local
  cwd: ~/system/second-brain
  timeout: 180
agent:
  max_turns: 90
  gateway_timeout: 1800
memory:
  memory_enabled: true
  user_profile_enabled: true
EOF

cat > ~/.hermes/.env << 'EOF'
LLM_API_KEY=sk-your-key-here
LLM_BASE_URL=https://api.anthropic.com
EOF

# 4. Test
hermes chat -q "Hello!"
```

📖 **Full guide**: [docs/QUICKSTART.md](docs/QUICKSTART.md)

---

## Architecture

```
~/system/
├── .venv/              # Python virtual environment (Hermes)
├── hermes/             # → symlink to ~/.hermes/ (config, skills, sessions)
└── second-brain/       # Your knowledge base (Obsidian vault)
    ├── raw/            # Source materials (never modify)
    │   └── inbox/      # Incoming files
    ├── wiki/           # Refined knowledge
    │   ├── concepts/   # Concept definitions
    │   ├── entities/   # People, companies, tools
    │   ├── sources/    # Source summaries
    │   └── synthesis/  # Cross-analysis
    └── scripts/        # Automation scripts
```

### How It Works

```
Drop file → raw/inbox/
    ↓
Hermes classifies → raw/articles/ | raw/papers/ | ...
    ↓
Hermes ingests → wiki/concepts/ | wiki/entities/ | wiki/sources/
    ↓
Wiki indexed → queryable via CLI, Discord, or Claude Code
```

---

## Documentation

| Doc | Description |
|-----|-------------|
| [Quick Start](docs/QUICKSTART.md) | Get running in 10 minutes |
| [Second Brain Setup](docs/second-brain-setup.md) | Knowledge base structure, Obsidian, templates |
| [Hermes Agent Setup](docs/hermes-agent-setup.md) | Skills, Discord, cron, operations |

---

## What You Need

- **Python 3.10+**
- **Git**
- **An LLM API key** (Anthropic, OpenAI, OpenRouter, or Ollama)
- **Obsidian** (optional, for visual editing)

---

## Credits

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research
- [Obsidian](https://obsidian.md) for the knowledge base UI

---

**License**: MIT
