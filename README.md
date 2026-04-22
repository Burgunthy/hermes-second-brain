# Hermes Second Brain

> Obsidian + Graphify + Claude Code + Hermes Agent — 하나의 LLM 기반 지식 관리 시스템

이 레포를 `~/system/` 에 복사하면, 어떤 LLM도 README만 읽고 동일한 시스템을 구축할 수 있습니다.

---

## 레포 구조 (= 실제 시스템 구조)

```
hermes-second-brain/
├── README.md                          # 이 파일
├── second-brain/                      # → ~/system/second-brain/ (Obsidian vault)
│   ├── CLAUDE.md                      # Claude Code 가이드
│   ├── .hermes.md                     # Hermes 프로젝트 컨텍스트
│   ├── raw/                           # 원본 자료 (수정 금지)
│   │   ├── inbox/                     # 미처리 수집품
│   │   ├── articles/                  # 웹 아티클
│   │   ├── papers/                    # 논문
│   │   └── notes/                     # 수동 메모
│   ├── wiki/                          # 정제된 지식 베이스
│   │   ├── index.md                   # 전체 목차
│   │   ├── log.md                     # 변경 이력
│   │   ├── concepts/                  # 개념 문서
│   │   ├── entities/                  # 실체 문서 (도구, 인물, 제품)
│   │   ├── sources/                   # 소스별 요약
│   │   └── synthesis/                 # 통합 분석
│   ├── graphify-out/                  # 지식 그래프 (wiki-graph.py 출력)
│   └── output/                        # 산출물
├── scripts/                           # → ~/system/scripts/
│   ├── wiki-graph.py                  # wiki → 지식 그래프 생성
│   └── wiki-lint.py                   # 위키 정합성 검사
├── hermes/                            # → ~/.hermes/skills/
│   └── skills/                        # Hermes 스킬
│       ├── daily-ingest/SKILL.md
│       ├── archive/SKILL.md
│       └── research/SKILL.md
└── kor/README.md                      # 한국어 번역
```

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
      └── 피드백 ──→ 수정 지시 ────────→ 반영
```

---

## 전제 조건

- **Ubuntu 22.04+** (Linux)
- **Python 3.10+**
- **Node.js 20+** (Playwright MCP용)
- **Claude Code** — `npm install -g @anthropic-ai/claude-code`
- **Git**, **pip + venv** — `sudo apt install git python3-pip python3-venv`

---

## 설치

### 1. 레포 복사

```bash
git clone https://github.com/Burgunthy/hermes-second-brain.git ~/system
```

### 2. Obsidian Vault 설정

Obsidian에서 "Open folder as vault" → `~/system/second-brain/` 선택.

### 3. Graphify (지식 그래프)

```bash
python3 ~/system/scripts/wiki-graph.py
# → graphify-out/graph.json, graph.html, stats.json 생성
```

### 4. Claude Code 설정

`second-brain/CLAUDE.md` 가 Claude Code에게 다음을 지시합니다:
- ❌ 직접 wiki/ 파일 수정 금지
- ✅ Hermes에게 작업 지시 → `hermes chat -q "..."`

```bash
cd ~/system/second-brain
claude
```

### 5. Hermes Agent 설치

```bash
# 가상환경
python3 -m venv ~/system/.venv
source ~/system/.venv/bin/activate

# Hermes (PyPI가 아님 — GitHub에서 직접)
pip install git+https://github.com/NousResearch/hermes-agent.git

# 의존성
pip install playwright
npx playwright install chromium
```

### 6. Hermes 설정

`~/.hermes/config.yaml`에서 반드시 수정할 항목:
- `model.default` → 사용할 모델
- `terminal.cwd` → `~/system/second-brain`

```bash
# API 키 환경변수로 토큰 설정
export DISCORD_BOT_TOKEN="***"
export OPENAI_API_KEY="***"
```

### 7. systemd 서비스 (상시 가동)

```bash
# ~/.config/systemd/user/hermes-gateway.service 생성 후:
systemctl --user daemon-reload
systemctl --user enable hermes-gateway
systemctl --user start hermes-gateway
systemctl --user status hermes-gateway
```

### 8. 스킬 배치

```bash
cp -r ~/system/hermes/skills/* ~/.hermes/skills/
```

---

## 자동화

### 일일 인제스트 (매일 새벽 4시)

```bash
hermes chat -q "크론잡 생성: daily-ingest, 0 4 * * *, raw/inbox/를 wiki/로 인제스트 후 graph 갱신, deliver: discord"
```

### 주간 린트 / 요약

```bash
hermes chat -q "크론잡 생성: weekly-lint, 0 5 * * 0, wiki-lint.py 실행 후 결과 보고"
hermes chat -q "크론잡 생성: weekly-summary, 0 9 * * 1, 지난 일주일 wiki 변경사항 요약"
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

- **raw/**: 절대 수정 금지 (원본 보존)
- **wiki/**: 정제 반영 시 `wiki/log.md`에 기록
- **wiki/index.md**: 항상 최신 상태 유지

---

## 라이선스

MIT

---

[한국어 README](kor/README.md)
