---
name: archive
description: Archive Discord messages to raw/inbox/ for the LLM Wiki system
tags: discord, archive, wiki, inbox
---

# Discord Archive Skill

Archive Discord messages to `raw/inbox/` for the LLM Wiki system.

## File Format

```markdown
---
source: discord
channel: {{channel_name}}
author: {{username}}
timestamp: {{timestamp}}
message_id: {{message_id}}
---

# Discord Archive: {{channel_name}}

**Author**: {{username}}
**Time**: {{timestamp}}

## Content

{{message_content}}
```

## Research Intent Detection

Check for research intent indicators:
- Keywords: "찾아", "검색", "조사", "깃허브", "github", "논문", "research", "search"
- Pattern: "/archive: [topic] [source]에서 찾아서 기록해"

When detected → Invoke `research` skill for parallel searches (GitHub, web, arXiv).
Simple archive → Save to `raw/inbox/` as-is.

## Configuration
- **Storage**: `~/system/second-brain/raw/inbox/`
- **Filename**: `YYYY-MM-DD-HHMMSS.md`
