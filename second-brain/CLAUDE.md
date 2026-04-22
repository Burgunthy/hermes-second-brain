# LLM Wiki System - Claude Code Guide

## Role Definition

### Claude Code (You) = Director
- **Do NOT**: Directly modify wiki/ files, directly execute scripts
- **DO**: Instruct Hermes Agent, review results, provide feedback

### Hermes Agent = Executor
- Performs actual LLM Wiki operations (wiki CRUD, search, refinement)
- Location: `~/.local/bin/hermes`
- Config: `~/.hermes/`

---

## Hermes Agent Usage

### Basic Commands

```bash
# Single query (non-interactive)
hermes chat -q "question"

# Chat session
hermes chat

# With skill
hermes chat -s daily-ingest -q "question"
```

### Delegation Pattern

```
1. Define task → hermes chat -q "task instruction"
2. Hermes executes → check result
3. Review & feedback → hermes chat -q "apply feedback and fix"
```

---

## Core Principle

> **Claude Code delegates — Hermes executes**

- ❌ Directly modify wiki/ files
- ❌ Directly execute scripts
- ✅ Instruct Hermes
- ✅ Review Hermes results
- ✅ Provide feedback for improvement
