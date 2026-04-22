# Second Brain 설정 가이드

> **Second Brain 지식 관리 시스템 전체 가이드**

---

## 목차

1. [개요](#개요)
2. [디렉토리 구조](#디렉토리-구조)
3. [Obsidian 설정](#obsidian-설정)
4. [Inbox Watcher](#inbox-watcher)
5. [인제스트 파이프라인](#인제스트-파이프라인)
6. [Git 워크플로우](#git-워크플로우)
7. [템플릿](#템플릿)

---

## 개요

Second Brain은 Obsidian과 Hermes Agent로 구동되는 구조화된 지식 베이스입니다.

```
파일 수신 → raw/inbox/
                    ↓
          Inbox Watcher가 분류
                    ↓
     raw/articles/ | raw/papers/ | raw/notes/ | ...
                    ↓
          Hermes가 wiki/로 인제스트
                    ↓
     wiki/concepts/ | wiki/entities/ | wiki/sources/
```

### 디렉토리 구조

```
~/system/second-brain/
├── .hermes.md                    # Hermes 프로젝트 컨텍스트
├── .gitignore
├── raw/                          # 원본 자료 (절대 수정 금지)
│   ├── inbox/                    # 미분류 수신 파일
│   ├── articles/                 # 웹 아티클, 블로그
│   ├── papers/                   # 논문
│   ├── notes/                    # 수동 메모
│   ├── meetings/                 # 회의록
│   ├── videos/                   # 영상 트랜스크립트
│   ├── code/                     # 코드 스니펫, 프로젝트
│   ├── research/                 # 리서치 노트
│   └── stock/                    # 주식/투자 노트
├── wiki/                         # 정제된 지식 베이스
│   ├── index.md                  # 마스터 인덱스 (Dataview)
│   ├── log.md                    # 변경 이력
│   ├── concepts/                 # 개념 정의
│   ├── entities/                 # 구조화된 엔티티
│   │   ├── persons/
│   │   ├── companies/
│   │   └── tools/
│   ├── sources/                  # 출처 요약
│   └── synthesis/                # 통합 분석
├── output/                       # 생성된 보고서
├── graphify-out/                 # 지식 그래프 출력
└── scripts/                      # 자동화 스크립트
    ├── hermes-ingest.sh
    ├── daily-ingest-flow.sh
    ├── inbox-watcher/
    │   ├── sort-all.sh
    │   ├── lib/
    │   └── logs/
    └── logs/
```

---

## Obsidian 설정

### 설치

1. https://obsidian.md 에서 다운로드
2. `~/system/second-brain`을 Vault로 열기

### 필수 플러그인

| 플러그인 | 용도 |
|----------|------|
| **Dataview** | wiki/index.md에서 동적 쿼리 |
| **Graph Analysis** (선택) | 위키 그래프 시각화 |

### 추천 설정

- **에디터**: `.md` 파일 소스 모드
- **파일 및 링크**: `[[위키링크]]` 형식 사용
- **외관**: 다크 테마 추천

---

## Inbox Watcher

Inbox Watcher는 `raw/inbox/`의 파일을 자동으로 적절한 하위 디렉토리로 분류합니다.

### 설정

```bash
cat > ~/system/second-brain/scripts/inbox-watcher/sort-all.sh << 'SCRIPT'
#!/bin/bash
# sort-all.sh — raw/inbox/의 모든 파일 분류
INBOX="$HOME/system/second-brain/raw/inbox"
LOG="$HOME/system/second-brain/scripts/inbox-watcher/logs"

mkdir -p "$LOG"

classify() {
    local file="$1"
    local name=$(basename "$file")
    local target="notes"  # 기본값

    case "$name" in
        *paper*|*논문*|*arxiv*)  target="papers" ;;
        *article*|*기사*|*블로그*) target="articles" ;;
        *meeting*|*회의*|*미팅*) target="meetings" ;;
        *video*|*영상*|*유튜브*) target="videos" ;;
        *code*|*코드*|*프로그래밍*) target="code" ;;
        *research*|*연구*|*조사*) target="research" ;;
        *stock*|*주식*|*투자*)    target="stock" ;;
    esac

    local dest="$HOME/system/second-brain/raw/$target"
    mkdir -p "$dest"
    mv "$file" "$dest/"
    echo "[$(date '+%Y-%m-%d %H:%M')] $name → $target" >> "$LOG/classify.log"
}

# inbox의 모든 .md 파일 처리
find "$INBOX" -maxdepth 1 -name "*.md" -type f | while read -r file; do
    classify "$file"
done
SCRIPT
chmod +x ~/system/second-brain/scripts/inbox-watcher/sort-all.sh
```

### 수동 실행

```bash
~/system/second-brain/scripts/inbox-watcher/sort-all.sh
```

---

## 인제스트 파이프라인

### 인제스트 스크립트 설치

```bash
cat > ~/system/second-brain/scripts/hermes-ingest.sh << 'SCRIPT'
#!/bin/bash
HERMES="$HOME/system/.venv/bin/hermes"
PROJECT_ROOT="$HOME/system/second-brain"
LOG_DIR="$PROJECT_ROOT/scripts/logs"
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_DIR/ingest.log"
}

ingest_file() {
    local file="$1"
    log "인제스트 중: $(basename "$file")"
    $HERMES chat -q "Ingest the file at $file into wiki/ following the .hermes.md instructions."
}

case "${1:-}" in
    --all)
        find "$PROJECT_ROOT/raw" -name "*.md" -type f | while read -r file; do
            ingest_file "$file"
        done
        ;;
    --file|-f)
        ingest_file "$2"
        ;;
    *)
        echo "사용법: $0 --all | --file <경로>"
        ;;
esac
SCRIPT
chmod +x ~/system/second-brain/scripts/hermes-ingest.sh
```

### 수동 인제스트

```bash
source ~/system/.venv/bin/activate
hermes chat -q "raw/inbox/topic.md를 wiki/로 인제스트해줘"
```

### 일괄 인제스트

```bash
~/system/second-brain/scripts/hermes-ingest.sh --all
```

### 전체 일일 플로우

1. Inbox Watcher가 새 파일 분류
2. Hermes가 분류된 파일을 wiki/로 인제스트
3. 위키 로그와 인덱스 업데이트

```bash
# 분류
~/system/second-brain/scripts/inbox-watcher/sort-all.sh

# 인제스트
~/system/second-brain/scripts/hermes-ingest.sh --all
```

---

## Git 워크플로우

```bash
cd ~/system/second-brain

# 상태 확인
git status

# 스테이징 및 커밋
git add -A
git commit -m "인제스트: wiki 항목 3개 추가"

# 원격 푸시 (선택)
git remote add origin git@github.com:YOURUSER/second-brain.git
git push -u origin main
```

### .gitignore

```gitignore
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
```

---

## 템플릿

### Wiki 개념 템플릿

```markdown
---
title: 개념명
type: concept
related: [[관련개념1]] [[관련개념2]]
sources: raw/원본경로.md
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [태그1, 태그2]
---

# 개념명

## 정의
...

## 핵심 포인트
- 포인트 1
- 포인트 2

## 관련
- [[관련개념1]] — 간단한 관계 설명
```

### Wiki 엔티티 템플릿

```markdown
---
title: 엔티티명
type: entity
subtype: person | company | tool
related: [[관련엔티티1]]
sources: raw/원본경로.md
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [태그1, 태그2]
---

# 엔티티명

## 개요
...

## 상세
...
```

### 출처 요약 템플릿

```markdown
---
title: 출처 제목
type: source_summary
related: [[개념1]] [[개념2]]
sources: raw/원본경로.md
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [태그1, 태그2]
---

# 출처 요약: 출처 제목

## TL;DR
...

## 핵심 인사이트
1. ...
2. ...

## 인용구
> "출처의 주요 인용문"
```

---

**버전**: 4.0.0 | **최종 업데이트**: 2026-04-22
