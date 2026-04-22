# 빠른 시작 가이드

> **10분 만에 Second Brain 구축**

---

## ⚠️ 시작 전 확인

다음이 필요합니다:
- **Python 3.10+** — `python3 --version` 확인
- **python3-venv** — Ubuntu/Debian: `sudo apt install python3-venv`
- **Git** — `git --version` 확인
- **LLM API 키** — Anthropic, OpenAI, 또는 OpenAI 호환 제공자

---

## 디렉토리 구조

설치 완료 후 `~/system/` 구조:

```
~/system/
├── .venv/              # Hermes 가상환경
├── hermes/             # → ~/.hermes/ 심링크 (설정, 세션, 스킬)
└── second-brain/       # 지식 베이스 (Obsidian vault)
```

---

## 1–2분: 지식 베이스 생성

```bash
# 전체 디렉토리 한 번에 생성
mkdir -p ~/system/second-brain/{raw/{inbox,articles,papers,notes,meetings,videos,code,research,stock},wiki/{concepts,entities/{persons,companies,tools},sources,synthesis},output,scripts/{inbox-watcher/lib,inbox-watcher/logs,logs}}

# Git 초기화
cd ~/system/second-brain
git init
git config user.email "you@example.com"
git config user.name "Your Name"

# .gitignore 생성
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

## 3–4분: Obsidian 설정

1. Obsidian 설치: https://obsidian.md
2. `~/system/second-brain`을 Vault로 열기
3. **설정 → 커뮤니티 플러그인** → 커뮤니티 플러그인 사용 활성화
4. **Dataview** 플러그인 설치 (wiki/index.md 동작에 필요)

---

## 5–6분: 기본 문서 생성

```bash
cd ~/system/second-brain

# 위키 로그
cat > wiki/log.md << 'EOF'
---
title: Wiki 변경 이력
type: log
---

# Wiki 변경 이력
EOF

# 위키 인덱스 (heredoc의 백틱 이스케이프 문제를 피하기 위해 python3 사용)
python3 -c "
content = '''---
title: Wiki 인덱스
type: index
---

# Wiki 인덱스

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

# inbox 테스트 파일
cat > raw/inbox/test.md << 'EOF'
# 테스트 노트

Second Brain 시스템의 첫 번째 노트입니다.
EOF
```

---

## 7–10분: Hermes Agent 설치

### 1단계: 가상환경 생성

```bash
# ~/system/ 내에 venv 생성
python3 -m venv ~/system/.venv
source ~/system/.venv/bin/activate
```

### 2단계: GitHub에서 Hermes 설치

Hermes는 PyPI에 없습니다 — GitHub에서 직접 설치:

```bash
pip install git+https://github.com/NousResearch/hermes-agent.git

# 확인
hermes --version
```

### 3단계: 설정

```bash
# 설정 디렉토리 생성 (최초 실행 시 Hermes도 생성)
mkdir -p ~/.hermes

# 접근 편의를 위해 ~/system/에 심링크 생성
ln -sf ~/.hermes ~/system/hermes

# config.yaml 생성
cat > ~/.hermes/config.yaml << 'EOF'
model:
  default: YOUR_MODEL_NAME    # 예: claude-sonnet-4, gpt-4o, glm-5.1
  providers: {}

terminal:
  backend: local
  cwd: ~/system/second-brain  # 지식 베이스 경로
  timeout: 180

agent:
  max_turns: 90
  gateway_timeout: 1800

memory:
  memory_enabled: true
  user_profile_enabled: true
EOF

# API 키로 .env 생성
cat > ~/.hermes/.env << 'EOF'
# 실제 API 키와 엔드포인트로 교체
LLM_API_KEY=sk-your-actual-api-key-here
LLM_BASE_URL=https://api.anthropic.com
EOF
chmod 600 ~/.hermes/.env
```

### 4단계: 프로젝트 컨텍스트 추가

```bash
cat > ~/system/second-brain/.hermes.md << 'EOF'
# Second Brain — Hermes 컨텍스트

## 목적
이 지식 베이스의 실행자입니다. 역할:
1. **검색**: wiki/에서 근거 기반 답변
2. **인제스트**: raw/ 파일을 구조화된 wiki/ 항목으로 변환
3. **유지보수**: 깨진 링크 수정, 중복 제거, 정합성 점검
4. **자동화**: 정기 작업 실행 (매일 인제스트, 매주 린트)

## 규칙
- raw/ 폴더는 절대 수정 금지
- wiki/ 변경 사항은 wiki/log.md에 기록
- [[위키링크]] 형식으로 출처 표시
EOF
```

### 5단계: 테스트

```bash
source ~/system/.venv/bin/activate
hermes chat -q "Hello! raw/inbox/에 뭐가 있어?"
```

✅ **완료!** Second Brain이 준비되었습니다.

---

## 경로 안내

| 경로 | 용도 |
|------|------|
| `~/system/.venv/` | Hermes가 설치된 Python 가상환경 |
| `~/system/hermes/` | 심링크 → `~/.hermes/` (설정, 스킬, 세션) |
| `~/system/second-brain/` | 지식 베이스 (Obsidian vault) |
| `~/.hermes/config.yaml` | Hermes 설정 |
| `~/.hermes/.env` | API 키 (비밀 보관!) |

---

## 다음 단계

- 📖 [**Second Brain 설정**](second-brain-setup.md) — Inbox Watcher, Obsidian 템플릿, 자동화 스크립트
- 🤖 [**Hermes Agent 설정**](hermes-agent-setup.md) — 스킬, Discord 연동, 크론 자동화
