# Hermes Agent 설정 가이드

> **Second Brain과 Hermes Agent 연동 전체 가이드**

---

## 목차

1. [개요](#개요)
2. [사전 요구사항](#사전-요구사항)
3. [1단계: Hermes 설치](#1단계-hermes-설치)
4. [2단계: API 제공자 설정](#2단계-api-제공자-설정)
5. [3단계: config.yaml 생성](#3단계-configyaml-생성)
6. [4단계: 프로젝트 컨텍스트 추가](#4단계-프로젝트-컨텍스트-추가)
7. [5단계: 스킬 생성](#5단계-스킬-생성)
8. [6단계: Hermes 시작](#6단계-hermes-시작)
9. [Discord 연동](#discord-연동)
10. [크론 자동화](#크론-자동화)
11. [운영 가이드](#운영-가이드)
12. [트러블슈팅](#트러블슈팅)

---

## 개요

Hermes는 Second Brain의 **실행자(Executor)** 역할을 하는 항시 가동 AI 에이전트입니다.

```
┌──────────────┐  ┌──────────┐  ┌──────────────┐
│   Discord    │  │   CLI    │  │ Claude Code  │
│    (사용자)   │  │ (사용자)  │  │  (감독자)     │
└──────┬───────┘  └────┬─────┘  └──────┬───────┘
       │               │               │
       └───────────────┼───────────────┘
                       ▼
              ┌─────────────────┐
              │  Hermes Agent   │
              │   (실행자)       │
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    위키 검색     Raw 인제스트    스크립트 실행
```

### 디렉토리 구조

```
~/system/
├── .venv/              # Python 가상환경
├── hermes/             # → ~/.hermes/ 심링크 (설정, 세션, 스킬)
└── second-brain/       # 지식 베이스 (Obsidian vault)
```

---

## 사전 요구사항

- **Python 3.10+**
- **python3-venv** - Ubuntu/Debian: `sudo apt install python3-venv`
- **Git**
- **LLM API 키** (지원 제공자)
- **Discord Bot** (선택, Discord 접근용)

---

## 1단계: Hermes 설치

```bash
# 가상환경 생성
python3 -m venv ~/system/.venv
source ~/system/.venv/bin/activate

# GitHub에서 설치 (PyPI에 없음)
pip install git+https://github.com/NousResearch/hermes-agent.git

# 확인
hermes --version

# 편의를 위해 alias 추가 (선택)
echo 'alias hermes="$HOME/system/.venv/bin/hermes"' >> ~/.bashrc
source ~/.bashrc
```

---

## 2단계: API 제공자 설정

Hermes에 LLM 제공자가 필요합니다. 하나를 선택하세요:

| 제공자 | API 키 형식 | Base URL | 예시 모델 |
|--------|-------------|----------|-----------|
| **Anthropic** | `sk-ant-...` | `https://api.anthropic.com` | `claude-sonnet-4` |
| **OpenAI** | `sk-...` | `https://api.openai.com/v1` | `gpt-4o` |
| **OpenRouter** | `sk-or-...` | `https://openrouter.ai/api/v1` | `anthropic/claude-sonnet-4` |
| **Ollama (로컬)** | 불필요 | `http://localhost:11434/v1` | `llama3` |

---

## 3단계: config.yaml 생성

```bash
# 설정 디렉토리 + 심링크 생성
mkdir -p ~/.hermes
ln -sf ~/.hermes ~/system/hermes

# .env에 API 키 생성
cat > ~/.hermes/.env << 'EOF'
LLM_API_KEY=sk-your-actual-key-here
LLM_BASE_URL=https://api.anthropic.com
EOF
chmod 600 ~/.hermes/.env

# config 생성
cat > ~/.hermes/config.yaml << 'EOF'
model:
  default: claude-sonnet-4       # ← 사용할 모델로 변경
  providers: {}

terminal:
  backend: local
  cwd: ~/system/second-brain    # ← 지식 베이스 경로
  timeout: 180

agent:
  max_turns: 90
  gateway_timeout: 1800

memory:
  memory_enabled: true
  user_profile_enabled: true
EOF
```

### 설정 레퍼런스

| 항목 | 필수 | 설명 |
|------|------|------|
| `model.default` | ✅ | 제공자의 모델명 |
| `model.providers` | 아니오 | 제공자별 오버라이드 |
| `terminal.cwd` | ✅ | Hermes가 작업하는 경로 (vault) |
| `terminal.timeout` | 아니오 | 쉘 명령어 타임아웃 (초) |

---

## 4단계: 프로젝트 컨텍스트 추가

Hermes는 `terminal.cwd` 디렉토리에서 `.hermes.md`를 읽습니다. 이 파일이 Hermes에게 역할과 규칙을 알려줍니다.

> ⚠️ 아래 `.hermes.md`에는 중첩 코드블록(프론트매터 예시)이 포함되어 있습니다. Bash heredoc으로 처리할 수 없으므로 Python 명령을 사용하세요:

```bash
python3 << 'PYEOF'
content = """# Second Brain - Hermes 컨텍스트

## 목적
이 지식 베이스의 실행자입니다. 역할:
1. **검색**: wiki/에서 근거 기반 답변
2. **인제스트**: raw/ 파일을 구조화된 wiki/ 항목으로 변환
3. **유지보수**: 깨진 링크 수정, 중복 제거, 정합성 점검
4. **자동화**: 정기 작업 실행 (매일 인제스트, 매주 린트)

## 디렉토리 맵
- `raw/` - 원본 자료 (절대 수정 금지)
- `raw/inbox/` - 미분류 수신 파일
- `wiki/concepts/` - 개념 정의
- `wiki/entities/` - 인물, 회사, 도구
- `wiki/sources/` - 출처 요약
- `wiki/synthesis/` - 통합 분석
- `wiki/log.md` - 변경 이력 (모든 wiki 수정 시 업데이트)
- `wiki/index.md` - 마스터 인덱스

## 인제스트 프로세스
raw/의 각 파일에 대해:
1. 파일 내용 읽기
2. 핵심 개념 추출 → `wiki/concepts/<이름>.md` 생성/업데이트
3. 엔티티 추출 (인물, 도구, 회사) → `wiki/entities/`
4. 출처 요약 작성 → `wiki/sources/<이름>.md`
5. 관련 문서 간 [[위키링크]] 추가
6. 변경 사항을 `wiki/log.md`에 기록
7. 새 카테고리가 추가되면 `wiki/index.md` 업데이트

## 규칙
- raw/ 파일은 절대 수정 금지
- wiki 파일에는 항상 YAML 프론트매터 추가
- [[위키링크]] 문법으로 출처 표시
- 불확실하면 "모르겠다"고 답변 - 절대 지어내지 마세요
- wiki/log.md를 항상 최신으로 유지

## 프론트매터 스키마
```yaml
title: 문서 제목
type: concept | entity | source_summary | synthesis
related: [[다른문서1]] [[다른문서2]]
sources: raw/원본경로.md
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [태그1, 태그2]
```
"""
with open("$HOME/system/second-brain/.hermes.md", "w") as f:
    f.write(content)
print("Created .hermes.md")
PYEOF
```

---

## 5단계: 스킬 생성

스킬은 Markdown 파일로 저장되는 재사용 가능한 명령어입니다. Hermes는 `~/.hermes/skills/`에서 스킬을 찾습니다 (`~/system/hermes/skills/`로도 접근 가능).

### 위키 검색 스킬

```bash
mkdir -p ~/.hermes/skills/wiki-query
cat > ~/.hermes/skills/wiki-query/SKILL.md << 'EOF'
---
name: wiki-query
description: Second Brain 위키 검색 및 질문 답변
---

# 위키 검색

## 단계
1. 사용자 질문에서 키워드 추출
2. `wiki/concepts/`와 `wiki/entities/`에서 일치 항목 검색
3. [[위키링크]]를 따라 관련 문서 탐색
4. 발견 내용을 구조화된 답변으로 종합

## 출력 형식
- 직접 답변으로 시작
- 근거 나열: `- [[출처문서]]: 간단한 요약`
- 지식의 빈틈이 있으면 명시
EOF
```

### 위키 인제스트 스킬

```bash
mkdir -p ~/.hermes/skills/wiki-ingest
cat > ~/.hermes/skills/wiki-ingest/SKILL.md << 'EOF'
---
name: wiki-ingest
description: raw 파일을 위키로 인제스트
---

# 위키 인제스트

## 단계
1. raw/에서 대상 파일 읽기
2. 유형 판별 (개념, 엔티티, 또는 출처)
3. 핵심 정보 추출
4. 적절한 프론트매터로 wiki 파일 생성
5. 기존 관련 문서에 [[위키링크]] 추가
6. wiki/log.md 업데이트
7. 필요시 wiki/index.md 업데이트

## 파일 배치
- 새 개념 → `wiki/concepts/<슬러그>.md`
- 새 엔티티 → `wiki/entities/<타입>/<슬러그>.md`
- 출처 요약 → `wiki/sources/<슬러그>.md`
EOF
```

### 위키 린트 스킬

```bash
mkdir -p ~/.hermes/skills/wiki-lint
cat > ~/.hermes/skills/wiki-lint/SKILL.md << 'EOF'
---
name: wiki-lint
description: 위키 정합성 점검 및 문제 수정
---

# 위키 린트

## 점검 항목
1. 깨진 [[위키링크]] - 대상 파일이 없음
2. 누락된 프론트매터 - YAML 헤더가 없는 파일
3. 오래된 `updated:` 날짜 - 최근 수정과 불일치
4. 고아 파일 - 수신 링크가 없는 위키 페이지
5. 중복 개념 - 여러 파일에 동일 주제

## 수정
- 존재하지 않는 파일 링크 제거
- 누락된 곳에 최소 프론트매터 추가
- 고아 파일은 수동 검토용으로 보고
- 내용이 겹치면 중복 병합
EOF
```

---

## 6단계: Hermes 시작

### CLI 모드 (1회성 쿼리)

```bash
# venv 활성화
source ~/system/.venv/bin/activate

# 단일 질문
hermes chat -q "raw/inbox/에 뭐가 있어?"

# 대화형 세션
hermes chat
```

### 데몬 모드 (항시 가동)

```bash
# 포그라운드로 게이트웨이 실행 (권장)
~/system/.venv/bin/hermes gateway run

# 또는 systemd 서비스로 시작
~/system/.venv/bin/hermes gateway install
~/system/.venv/bin/hermes gateway start

# 상태 확인
~/system/.venv/bin/hermes gateway status
```

### Systemd (Linux, 자동 시작)

Hermes에 내장된 systemd 설치기를 사용하는 것이 좋습니다 - 위의 `hermes gateway install`을 참조하세요.

또는 수동 생성:

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

> ⚠️ `YOURUSER`를 실제 사용자명으로 변경하세요.

---

## Discord 연동

### Discord Bot 생성

1. **[Discord Developer Portal](https://discord.com/developers/applications)** 이동
2. **"New Application"** 클릭 → 이름 지정 (예: "Second Brain Bot")
3. **"Bot"** 탭 → **"Reset Token"** → 토큰 복사
4. **Privileged Gateway Intents** 활성화:
   - ✅ **Message Content Intent** (필수)
   - ✅ **Server Members Intent** (선택)
5. **"OAuth2"** → **"URL Generator"**:
   - Scopes: `bot`
   - Permissions: Send Messages, Read Messages, Add Reactions, Attach Files, Embed Links
   - 생성된 URL로 서버에 초대

### Discord 설정

```bash
# ~/.hermes/.env에 추가
cat >> ~/.hermes/.env << 'EOF'
DISCORD_BOT_TOKEN=your-bot-token-here
DISCORD_ALLOWED_USERS=your-discord-user-id
EOF
chmod 600 ~/.hermes/.env
```

`~/.hermes/config.yaml`에 Discord 섹션 추가:

```yaml
discord:
  require_mention: true
  allowed_channels: ""
  auto_thread: true
  reactions: true
```

---

## 크론 자동화

### 인제스트 스크립트

> 인제스트 스크립트는 [Second Brain 설정 → 인제스트 파이프라인](./second-brain-setup.md#인제스트-파이프라인)에 정의되어 있습니다. 아직 설정하지 않았다면 먼저 해당 가이드를 따르세요.

### 크론 설정

```bash
crontab -e

# 다음 줄 추가:
# 매일 새벽 4시: 인제스트
0 4 * * * $HOME/system/.venv/bin/hermes chat -q "Ingest everything in raw/inbox/"

# 매주 일요일 새벽 3시: 위키 린트
0 3 * * 0 $HOME/system/.venv/bin/hermes chat -q "Run wiki-lint on the entire wiki/ directory."
```

---

## 운영 가이드

### 일일

```bash
source ~/system/.venv/bin/activate
hermes chat -q "raw/inbox/에 뭐가 있어?"
hermes chat -q "raw/inbox/의 모든 파일을 인제스트해줘"
```

### 주간

```bash
hermes chat -s wiki-lint -q "전체 위키 정합성 점검"
```

### 유용한 경로

| 항목 | 경로 |
|------|------|
| venv 활성화 | `source ~/system/.venv/bin/activate` |
| 설정 | `~/.hermes/config.yaml` 또는 `~/system/hermes/config.yaml` |
| API 키 | `~/.hermes/.env` |
| 스킬 | `~/.hermes/skills/` 또는 `~/system/hermes/skills/` |
| 지식 베이스 | `~/system/second-brain/` |
| 게이트웨이 로그 | `~/system/hermes/logs/` |

---

## 트러블슈팅

### `hermes` 명령어를 찾을 수 없음
```bash
source ~/system/.venv/bin/activate
# 또는 전체 경로: ~/system/.venv/bin/hermes
```

### API 키 에러
```bash
cat ~/.hermes/.env
# LLM_API_KEY에 실제 키가 있는지 확인
```

### Discord에서 Hermes 응답 없음
1. Discord 서버에 봇이 온라인인지 확인
2. `~/.hermes/.env`에서 `DISCORD_BOT_TOKEN` 확인
3. Developer Portal에서 Message Content Intent 활성화 확인
4. 로그 확인: `~/system/.venv/bin/hermes logs`

---

## 설정 체크리스트

- [ ] Python 3.10+ 설치됨
- [ ] `~/system/.venv/`에 Hermes 설치됨
- [ ] `~/.hermes/.env`에 실제 API 키 있음
- [ ] `~/.hermes/config.yaml`에 올바른 모델 + `cwd: ~/system/second-brain`
- [ ] `~/system/hermes` 심링크 존재 → `~/.hermes/`
- [ ] `~/system/second-brain/` 디렉토리 구조 생성됨
- [ ] `~/system/second-brain/.hermes.md` 프로젝트 컨텍스트 추가됨
- [ ] 스킬 생성됨 (wiki-query, wiki-ingest, wiki-lint)
- [ ] `hermes chat -q "Hello"` 동작 확인
- [ ] (선택) Discord Bot 설정됨
- [ ] (선택) 크론 잡 설정됨

---

**버전**: 4.0.0 | **최종 업데이트**: 2026-04-22
