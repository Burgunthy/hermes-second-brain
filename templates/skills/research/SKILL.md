---
name: research
description: Research and fetch information from GitHub, web, arXiv
tags: research, search, github, arxiv, web
---

# Research Skill

Multi-source research triggered by `/archive` research intent detection.

## How It Works

1. Archive skill detects research intent
2. Parallel searches across:
   - GitHub (repositories, issues, wiki)
   - Web (Brave Search API)
   - arXiv (academic papers)
3. Results aggregated and formatted
4. Summary sent to Discord + full data saved to `raw/inbox/`

## Configuration

API keys required (via environment variables):
- `BRAVE_API_KEY` (required for web search)
- `GITHUB_TOKEN` (optional, for higher rate limits)
- arXiv: no API key needed

## Output
- Discord: Search results summary (top 5 per source)
- `raw/inbox/`: Full results for wiki ingest
