# Hermes Second Brain

> Obsidian + Graphify + Claude Code + Hermes Agent — 하나의 LLM 기반 지식 관리 시스템

한 개의 README와 `templates/` 디렉토리만으로, 어떤 LLM도 동일한 시스템을 구축할 수 있도록 설계했습니다.

---

## 목차

- [시스템 개요](#시스템-개요)
- [디렉토리 구조](#디렉토리-구조)
- [전제 조건](#전제-조건)
- [Step 1: Obsidian Vault 설정](#step-1-obsidian-vault-설정)
- [Step 2: Graphify — 지식 그래프 생성](#step-2-graphify--지식-그래프-생성)
- [Step 3: Claude Code — 감독(Director) 설정](#step-3-claude-code--감독director-설정)
- [Step 4: Hermes Agent — 실행자(Executor) 설정](#step-4-hermes-agent--실행자executor-설정)
- [자동화](#자동화)
- [운영 가이드](#운영-가이드)

---

## 시스템 개요

4개 컴포넌트가 하나로 연결된 복리형 지식 관리 시스템입니다:

| 컴포넌트 | 역할 | 위치 |
|----------|------|------|
| **Obsidian** | 지식 베이스 저장소 (vault) | `~/system/second-brain/` |
| **Graphify** | 위키링크 → 지식 그래프 시각화 | `~/system/scripts/wiki-graph.py` |
| **Claude Code** | 감독 — 복잡한 인제스트, 시스템 설계 | 로컬 터미널 (IDE) |
| **Hermes Agent** | 실행자 — 수집, 인제스트, 크론 자동화 | 서버 상주 + Discord/CLI |

**핵심 원칙**: Claude Code는 직접 파일을 만지지 않고 Hermes에게 지시합니다. Hermes가 실제 작업을 수행합니다.

```
Claude Code (Director)          Hermes Agent (Executor)
      │                                │
      │── "wiki 인제스트 해줘" ────────→ wiki/ CRUD, 검색, 크론
      │←── 결과 보고 ──────────────────│
      │                                │
      └── 피드백 ──→ 수정 지시 ────────→ 반영
```

---

## 디렉토리 구조

```
~/system/
├── .venv/                          # Python 가상환경
├── scripts/                        # 시스템 스크립트
│   ├── wiki-graph.py               # Graphify: wiki → 지식 그래프
│   ├── wiki-lint.py                # 위키 정합성 검사
│   └── daily-ingest-flow.sh        # 일일 인제스트 파이프라인
├── second-brain/                   # Obsidian vault (지식 베이스)
│   ├── .hermes.md                  # Hermes 프로젝트 컨텍스트
│   ├── CLAUDE.md                   # Claude Code 가이드
│   ├── raw/                        # 원본 자료 (수정 금지)
│   │   ├── inbox/                  # 미처리 수집품
│   │   ├── articles/               # 웹 아티클
│   │   ├── papers/                 # 논문
│   │   └── notes/                  # 수동 메모
│   ├── wiki/                       # 정제된 지식 베이스
│   │   ├── index.md                # 전체 목차
│   │   ├── log.md                  # 변경 이력
│   │   ├── concepts/               # 개념 문서 (LLM Wiki, RAG 등)
│   │   ├── entities/               # 실체 문서 (도구, 인물, 제품)
│   │   └── sources/                # 소스별 요약
│   ├── graphify-out/               # 지식 그래프 산출물
│   │   ├── graph.json              # 노드 + 엣지 구조
│   │   └── graph.html              # vis.js 인터랙티브 시각화
│   └── output/                     # 산출물 (보고서, 스크립트)
└── hermes/                         # → ~/.hermes/ (심링크)
    ├── config.yaml                 # Hermes 설정
    ├── SOUL.md                     # 시스템 프롬프트
    ├── skills/                     # 스킬 (재사용 가능한 워크플로우)
    └── cron/                       # 크론잡 상태
```

`templates/` 디렉토리에 각 설정 파일의 실제 동작 예시가 있습니다. 복사해서 바로 사용할 수 있습니다.

---

## 전제 조건

- **Ubuntu 22.04+** (Linux)
- **Python 3.10+**
- **Node.js 20+** (Playwright MCP용)
- **Claude Code** — Anthropic CLI (`npm install -g @anthropic-ai/claude-code`)
- **Git** — `sudo apt install git`
- **pip + venv** — `sudo apt install python3-pip python3-venv`

---

## Step 1: Obsidian Vault 설정

### 1-1. 디렉토리 생성

```bash
mkdir -p ~/system/second-brain/{raw/{inbox,articles,papers,notes},wiki/{concepts,entities,sources,synthesis},graphify-out,output}
mkdir -p ~/system/scripts
```

### 1-2. 설정 파일 배치

```bash
# .hermes.md — Hermes 프로젝트 컨텍스트 (templates/hermes.md 참고)
cp templates/hermes.md ~/system/second-brain/.hermes.md

# CLAUDE.md — Claude Code 가이드 (templates/CLAUDE.md 참고)
cp templates/CLAUDE.md ~/system/second-brain/CLAUDE.md
```

### 1-3. 초기 wiki 파일

`wiki/index.md`를 생성합니다:

```bash
python3 -c "
content = '''---
title: LLM Wiki Index
type: index
created: $(date +%Y-%m-%d)
updated: $(date +%Y-%m-%d)
---

# Wiki Index

## Concepts

## Entities

## Sources
'''
with open('$HOME/system/second-brain/wiki/index.md', 'w') as f:
    f.write(content)
"
```

`wiki/log.md`를 생성합니다:

```bash
python3 -c "
content = '''---
title: Wiki Change Log
type: log
created: $(date +%Y-%m-%d)
updated: $(date +%Y-%m-%d)
---

# Change Log

## $(date +%Y-%m-%d)
- System initialized
'''
with open('$HOME/system/second-brain/wiki/log.md', 'w') as f:
    f.write(content)
"
```

### 1-4. Obsidian으로 열기

Obsidian에서 "Open folder as vault" → `~/system/second-brain/` 선택.

---

## Step 2: Graphify — 지식 그래프 생성

Graphify는 `wiki/`의 마크다운 파일에서 `[[wikilink]]`를 추출하여 지식 그래프를 생성하는 Python 스크립트입니다.

### 2-1. 스크립트 배치

```bash
cp templates/wiki-graph.py ~/system/scripts/wiki-graph.py
chmod +x ~/system/scripts/wiki-graph.py
```

### 2-2. 경로 수정

`wiki-graph.py` 내부의 `base_path`를 실제 환경에 맞게 수정:

```python
base_path = Path.home() / 'system' / 'second-brain'
```

### 2-3. 실행

```bash
python3 ~/system/scripts/wiki-graph.py
```

출력:
- `graphify-out/graph.json` — 노드(pages) + 엣지(wikilinks) 구조의 JSON
- `graphify-out/graph.html` — vis.js 기반 인터랙티브 네트워크 시각화 (브라우저에서 열기)
- `graphify-out/stats.json` — 노드/엣지 수, 타입별 통계

### 2-4. 작동 방식

1. `wiki/` 전체 스캔 → frontmatter에서 title, type 추출
2. 본문에서 위키링크 `[[Title]]` 추출 → 엣지 생성
3. 노드(문서) + 엣지(참조) → JSON 그래프 빌드
4. vis.js Network로 HTML 뷰어 생성

---

## Step 3: Claude Code — 감독(Director) 설정

Claude Code는 복잡한 인제스트, 스킬 생성, 시스템 설계를 담당합니다. 직접 wiki/를 수정하지 않고 Hermes에게 지시합니다.

### 3-1. CLAUDE.md 배치

`templates/CLAUDE.md`를 vault 루트에 배치합니다 (Step 1-2에서 이미 완료).

이 파일이 Claude Code에게 다음을 지시합니다:
- ❌ 직접 wiki/ 파일 수정 금지
- ❌ 직접 스크립트 실행 금지
- ✅ Hermes에게 작업 지시
- ✅ Hermes 결과 검토 및 피드백

### 3-2. Claude Code 사용법

```bash
# Claude Code를 vault 디렉토리에서 실행
cd ~/system/second-brain
claude
```

Claude Code 세션에서 Hermes에게 지시:

```
Hermes에게 wiki 인제스트를 실행하라고 지시해줘. raw/inbox/에 파일이 3개 있어.
```

Claude Code가 다음 명령으로 Hermes에게 위임:

```bash
hermes chat -q "raw/inbox/의 파일들을 wiki/로 인제스트해줘"
```

### 3-3. Claude Code 설정 (선택)

`.claude/settings.local.json`에 권한을 추가할 수 있습니다:

```json
{
  "permissions": {
    "allow": [
      "Bash(hermes chat -q:*)"
    ]
  }
}
```

---

## Step 4: Hermes Agent — 실행자(Executor) 설정

Hermes Agent는 항시 가동되며 Discord/CLI에서 접근 가능한 AI 비서입니다. 수집, 인제스트, 크론 자동화를 담당합니다.

### 4-1. 설치

```bash
# 가상환경 생성
python3 -m venv ~/system/.venv
source ~/system/.venv/bin/activate

# Hermes 설치 (PyPI가 아닌 GitHub에서 직접)
pip install git+https://github.com/NousResearch/hermes-agent.git

# 필수 의존성
pip install playwright
npx playwright install chromium
```

### 4-2. 설정

```bash
# 설정 디렉토리 생성 (또는 심링크)
mkdir -p ~/.hermes/skills

# 심링크 (선택 — ~/system/hermes/와 ~/.hermes/를 동기화)
ln -sf ~/system/hermes ~/.hermes

# config.yaml 배치
cp templates/config.yaml ~/.hermes/config.yaml
```

### 4-3. config.yaml 필수 설정

`config.yaml`에서 반드시 설정해야 할 항목:

```yaml
model:
  default: <your-model>           # e.g., glm-5-turbo, claude-sonnet-4

terminal:
  cwd: ~/system/second-brain      # 작업 디렉토리를 vault로 설정

discord:
  require_mention: true
  auto_thread: true

mcp_servers:
  playwright:                     # 웹 자동화용 (선택)
    command: npx
    args:
      - -y
      - '@playwright/mcp'
      - --headless
```

API 키는 환경변수로 설정:

```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 4-4. SOUL.md (시스템 프롬프트)

`~/.hermes/SOUL.md`에 Hermes의 기본 페르소나를 설정합니다. `templates/SOUL.md`를 참고하세요.

### 4-5. Discord 연결

```bash
# Discord 봇 토큰 설정
export DISCORD_BOT_TOKEN="MTQ3Mj..."

# 게이트웨이 시작
hermes gateway run
```

### 4-6. systemd 서비스로 상시 가동

```bash
# 서비스 파일 생성
python3 -c "
service = '''[Unit]
Description=Hermes Agent Gateway - Messaging Platform Integration
After=network.target
StartLimitIntervalSec=600
StartLimitBurst=5

[Service]
Type=simple
ExecStart=$(which python3) -m hermes_cli.main gateway run --replace
WorkingDirectory=$(python3 -c 'import hermes_cli; import os; print(os.path.dirname(hermes_cli.__file__))')
Environment=\"PATH=$(dirname $(which python3)):/usr/local/bin:/usr/bin:/bin\"
Environment=\"VIRTUAL_ENV=$VIRTUAL_ENV\"
Environment=\"HERMES_HOME=$HOME/system/hermes\"
Restart=always
RestartSec=30

[Install]
WantedBy=default.target
'''
with open('$HOME/.config/systemd/user/hermes-gateway.service', 'w') as f:
    f.write(service)
"

# 서비스 활성화
systemctl --user daemon-reload
systemctl --user enable hermes-gateway
systemctl --user start hermes-gateway

# 상태 확인
systemctl --user status hermes-gateway
```

### 4-7. 스킬 배치

`templates/skills/`에서 필요한 스킬을 `~/.hermes/skills/`에 복사:

```bash
# 일일 인제스트 스킬
cp -r templates/skills/daily-ingest ~/.hermes/skills/

# 아카이브 스킬 (Discord 메시지 → raw/inbox/)
cp -r templates/skills/archive ~/.hermes/skills/

# 리서치 스킬 (GitHub, arXiv, Web 검색)
cp -r templates/skills/research ~/.hermes/skills/
```

### 4-8. Hermes 명령어

```bash
# 단일 질의 (non-interactive)
hermes chat -q "질문"

# 채팅 세션
hermes chat

# 스킬 지정
hermes chat -s daily-ingest -q "인제스트 실행해"

# 게이트웨이 상태
hermes gateway status
```

---

## 자동화

### 일일 인제스트 (매일 새벽 4시)

Hermes 크론잡으로 설정:

```bash
hermes chat -q "다음 크론잡을 생성해:
- 이름: daily-ingest
- 스케줄: 매일 새벽 4시 (0 4 * * *)
- 프롬프트: raw/inbox/를 스캔하고, 파일을 읽어서 wiki/concepts/ 또는 wiki/entities/에 인제스트. wiki/index.md와 wiki/log.md 업데이트. 그 후 python3 ~/system/scripts/wiki-graph.py 실행.
- deliver: discord (홈 채널)"
```

### 주간 린트 (매주 일요일)

```bash
hermes chat -q "크론장 생성: weekly-lint, 매주 일요일 오전 5시, wiki-lint.py 실행 후 결과 보고"
```

### 주간 요약 (매주 월요일)

```bash
hermes chat -q "크론장 생성: weekly-summary, 매주 월요일 오전 9시, 지난 일주일 wiki 변경사항 요약"
```

---

## 운영 가이드

### 인제스트 프로세스

```
raw/ 파일 → 개념/엔티티 추출 → wiki/concepts/ 또는 wiki/entities/
        → wiki/sources/ 요약 생성
        → wiki/index.md 업데이트
        → wiki/log.md 기록
```

### wiki/ 문서 메타데이터

모든 wiki 문서는 다음 frontmatter를 포함합니다:

```yaml
---
title: 문서 제목
type: concept | entity | source_summary | synthesis
related: "[[관련문서1]] [[관련문서2]]"
sources: raw/파일경로.md
created: 2026-04-22
updated: 2026-04-22
---
```

### 파일 수정 규칙

- **raw/ 폴더**: 절대 수정 금지 (원본 보존)
- **wiki/ 폴더**: 정제 반영 시 `wiki/log.md`에 기록
- **wiki/index.md**: 항상 최신 상태 유지

### Claude Code ↔ Hermes 역할 분담

| 구분 | Claude Code | Hermes |
|------|-------------|--------|
| 역할 | 감독 (Director) | 실행자 (Executor) |
| 위치 | 로컬 터미널 | 서버 상주 + 멀티 플랫폼 |
| 작업 | 복잡한 인제스트, 스킬 생성, 시스템 설계 | 빠른 수집, 간단 인제스트, 크론 자동화 |
| 접근 | 터미널, IDE | Discord, CLI |

---

## 라이선스

MIT

---

## 한국어 버전

[Korean README](kor/README.md)
