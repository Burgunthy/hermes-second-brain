# Second Brain with Hermes Agent

> **자기 자신을 개선하는 지식 베이스를 구축하세요.**

항시 가동되는 AI 지식 관리 시스템:
- **Obsidian** — 위키 스타일 링킹이 가능한 구조화된 지식 베이스
- **Hermes Agent** — 지식을 수집, 검색, 유지보수하는 AI
- **크론 자동화** — 매일 인제스트, 매주 린트, 무인 운영

---

## 빠른 시작

```bash
# 1. 지식 베이스 생성
mkdir -p ~/system/second-brain/{raw/{inbox,articles,papers,notes,meetings,videos,code,research,stock},wiki/{concepts,entities/{persons,companies,tools},sources,synthesis},output,scripts/{inbox-watcher/lib,inbox-watcher/logs,logs}}
cd ~/system/second-brain && git init && git config user.email "you@example.com" && git config user.name "Your Name"

# 2. Hermes 설치
python3 -m venv ~/system/.venv
source ~/system/.venv/bin/activate
pip install git+https://github.com/NousResearch/hermes-agent.git

# 3. 설정
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

# 4. 테스트
hermes chat -q "Hello!"
```

📖 **전체 가이드**: [docs/QUICKSTART.md](docs/QUICKSTART.md) | 🇰🇷 [kor/QUICKSTART.md](QUICKSTART.md)

---

## 아키텍처

```
~/system/
├── .venv/              # Python 가상환경 (Hermes)
├── hermes/             # → ~/.hermes/ 심링크 (설정, 세션, 스킬)
└── second-brain/       # 지식 베이스 (Obsidian vault)
    ├── raw/            # 원본 자료 (절대 수정 금지)
    │   └── inbox/      # 수신 파일
    ├── wiki/           # 정제된 지식
    │   ├── concepts/   # 개념 정의
    │   ├── entities/   # 인물, 회사, 도구
    │   ├── sources/    # 출처 요약
    │   └── synthesis/  # 통합 분석
    └── scripts/        # 자동화 스크립트
```

### 동작 원리

```
파일 추가 → raw/inbox/
    ↓
Hermes가 분류 → raw/articles/ | raw/papers/ | ...
    ↓
Hermes가 인제스트 → wiki/concepts/ | wiki/entities/ | wiki/sources/
    ↓
위키 인덱스 완성 → CLI, Discord, Claude Code에서 검색 가능
```

---

## 문서

| 문서 | 설명 |
|------|------|
| [Quick Start](../docs/QUICKSTART.md) | 10분 만에 세팅 | 🇰🇷 [한국어](QUICKSTART.md) |
| [Second Brain Setup](../docs/second-brain-setup.md) | 지식 베이스 구조, Obsidian, 템플릿 | 🇰🇷 [한국어](second-brain-setup.md) |
| [Hermes Agent Setup](../docs/hermes-agent-setup.md) | 스킬, Discord, 크론, 운영 | 🇰🇷 [한국어](hermes-agent-setup.md) |

---

## 필요한 것

- **Python 3.10+**
- **python3-venv** — Ubuntu/Debian: `sudo apt install python3-venv`
- **Git**
- **LLM API 키** (Anthropic, OpenAI, OpenRouter, Ollama)
- **Obsidian** (선택, 시각적 편집용)

---

## 크레딧

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research
- [Obsidian](https://obsidian.md) 지식 베이스 UI

---

**라이선스**: MIT
