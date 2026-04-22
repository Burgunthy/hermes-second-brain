---
name: research
description: Research and fetch information from GitHub, web, arXiv
tags: research, search, github, arxiv, web
---

# Research Skill

Multi-source research triggered by `/archive` research intent detection.

## How It Works

1. Archive skill detects research intent
2. Parallel searches: GitHub, Web (Brave Search API), arXiv
3. Results aggregated and formatted
4. Summary sent to Discord + full data saved to `raw/inbox/`

## Configuration

API keys (via environment variables):
- `BRAVE_API_KEY` (required for web search)
- `GITHUB_TOKEN` (optional, higher rate limits)
- arXiv: no API key needed
