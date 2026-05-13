# Context 자동화 시스템 설정 가이드

> 슬랙 이모지(📌) / 노션 DB 체크박스로 `deeple-context`를 자동 관리하는 시스템

## 아키텍처

```
[Slack #decisions] ──📌──▶ [Event API] ────┐
[Slack #cs-policy] ──📌──▶ [Event API] ────┼──▶ [Lambda] ──AI analyze──▶ [GitHub API] ──▶ [deeple-context]
[Notion 기획 DB] ──🔄──▶ [EventBridge Cron 00:00] ────┘
```

| 모듈 | 파일 | 역할 |
|------|------|------|
| AI Analyzer | `context_analyzer.py` | 기존 context 구조 분석 + LLM으로 최적 경로/파일명/병합여부 결정 |
| Git Operator | `context_git.py` | GitHub Contents API로 파일 직접 쓰기/커밋 (git 바이너리 불필요) |
| Slack Extractor | `context_extractor.py` | Slack Thread 메시지 수집 및 마크다운 변환 |
| Event Processor | `event_processor.py` | 📌 이모지 이벤트 수신 + 채널 필터링 + 중복 방지 |
| Cron Handler | `cron_handler.py` | 자정 노션 DB 폴리싱 + target_path 저장 + synced_at 갱신 |
| Notion Converter | `notion_converter.py` | Notion Block → Markdown 변환 |
| Save Handler | `context_save_handler.py` | 전체 저장 파이프라인 오케스트레이션 |

---

## 1. Slack Event API 설정

### 1.1 권한 (OAuth Scopes)

| Scope | 이유 |
|-------|------|
| `commands` | Slash Command (`/context-save`) 사용 |
| `chat:write` | 저장 완료/실패 메시지 전송 |
| `reactions:read` | 📌 이모지 반응 감지 (핵심) |
| `channels:history` | 공개 채널 스레드 메시지 읽기 |
| `groups:history` | 프라이빗 채널 스레드 메시지 읽기 |
| `im:history` | DM 스레드 읽기 |
| `mpim:history` | 멀티 DM 스레드 읽기 |

### 1.2 Event Subscriptions

**Request URL**: `https://your-lambda-url/`

Subscribe to bot events:
- `reaction_added` ✅

> 처음 등록 시 Slack이 `url_verification` challenge를 볃. Lambda가 challenge를 그대로 반환하면 활성화됩니다.

### 1.3 환경변수

```bash
SLACK_BOT_TOKEN=xoxb-...           # Bot User OAuth Token
SLACK_CONTEXT_CHANNELS=C123,C456   # 📌 트리거를 허용할 채널 ID (쉼표 구분)
```

> 채널 ID는 Slack 웹/앱에서 채널명 우클릭 → "채널 세부정보 보기" → 하단에 `채널 ID`로 확인

---

## 2. 이모지 트리거 사용법

### 지정된 채널에서만 동작
```
#decisions, #cs-policy 등 SLACK_CONTEXT_CHANNELS에 등록된 채널
```

### 사용 흐름
```
1. 메시지 작성 (또는 기존 메시지)
2. 해당 메시지에 📌 (pushpin) 이모지 반응 추가
3. Lambda가 이벤트 수신 → 스레드 전체 수집 → AI 분석 → context 저장
4. (선택) 결과를 DM으로 알림
```

### 중복 방지
`_sync/slack-pins.log`에 처리된 `channel_id/message_ts`를 기록하여 중복 저장을 방지합니다.

---

## 3. Notion Database 설정

### 3.1 Integration 생성
1. [www.notion.so/my-integrations](https://www.notion.so/my-integrations) → New integration
2. 이름: `Context Automation`
3. **Internal Integration Token** 복사 → `NOTION_TOKEN` 환경변수

### 3.2 Database 스키마

"기획 문서 DB" (또는 기존 DB)에 다음 속성을 추가합니다:

| 속성명 | 타입 | 설명 |
|--------|------|------|
| `sync_to_context` | Checkbox | ✅ 체크 시 자정에 동기화 대상 |
| `target_path` | Text | 사용자 지정 저장 경로 (예: `dmand/cs/refund-policy.md`) |
| `synced_at` | Date | 마지막 동기화 일자 (시스템 자동 기록) |

> `target_path`가 비어있으면 AI가 자동으로 경로를 분석합니다.

### 3.3 페이지 공유
- 동기화할 Database 페이지 상단 `⋯` → `Add connections` → `Context Automation` 선택

### 3.4 환경변수

```bash
NOTION_TOKEN=secret_...
NOTION_PLANNING_DB_ID=12345678-1234-1234-1234-123456789abc
```

> Database ID는 Notion 페이지 URL에서 추출: `https://www.notion.so/deeplehr/12345678-1234-1234-1234-123456789abc`

---

## 4. GitHub Token 설정

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. `repo` scope 선택 (private repo 접근용)
3. 토큰 복사 → `GITHUB_TOKEN` 환경변수

```bash
GITHUB_TOKEN=ghp_...
CONTEXT_REPO_OWNER=DeepLeHR      # 선택
CONTEXT_REPO_NAME=deeple-context # 선택
CONTEXT_BRANCH=main              # 선택
```

---

## 5. AWS EventBridge Cron 설정

매일 자정(KST)에 Lambda를 트리거하여 Notion DB를 폴리싱합니다.

### 5.1 EventBridge Rule 생성
```json
{
  "name": "context-sync-daily-midnight-kst",
  "schedule": "cron(0 15 * * ? *)",
  "target": {
    "arn": "arn:aws:lambda:ap-northeast-2:ACCOUNT:function:slack-bot",
    "input": "{\"source\":\"aws.events\"}"
  }
}
```

> KST 자정 = UTC 15:00

### 5.2 Lambda 트리거 권한 추가
EventBridge가 Lambda를 invoke할 수 있도록 권한을 추가합니다.

---

## 6. Lambda 환경변수 총정리

| 변수명 | 필수 | 설명 |
|--------|------|------|
| `OPENAI_API_KEY` | ✅ | GPT-4o-mini 분석용 |
| `GITHUB_TOKEN` | ✅ | GitHub API 인증 |
| `SLACK_BOT_TOKEN` | ✅ | Slack API 인증 |
| `SLACK_CONTEXT_CHANNELS` | ✅ | 📌 트리거 채널 ID 목록 (쉼표 구분) |
| `NOTION_TOKEN` | ✅ | Notion API 인증 |
| `NOTION_PLANNING_DB_ID` | ✅ | 기획 문서 DB ID |
| `CONTEXT_REPO_OWNER` | ❌ | 기본 `DeepLeHR` |
| `CONTEXT_REPO_NAME` | ❌ | 기본 `deeple-context` |
| `CONTEXT_BRANCH` | ❌ | 기본 `main` |

---

## 7. deeple-context 메타데이터 구조

자동 동기화된 파일들은 다음 구조로 관리됩니다:

```
deeple-context/
├── _sync/
│   ├── notion-mapping.yaml    ← Notion page ID ↔ 파일 경로 매핑
│   └── slack-pins.log         ← 처리된 Slack 메시지 ts 기록
├── dmand/
│   └── cs/
│       └── refund-policy.md   ← 헤더: <!-- Source: notion.so/... | Synced: ... -->
└── ...
```

---

## 8. AI 배치 원칙

자동 분석 시 다음 기준으로 경로를 결정합니다:

1. **서비스 구분**: `dmand` / `gocho` / `shared` / `new`
2. **카테고리**: `domain`, `cs`, `policy`, `glossary`, `service`, `faq`, `meeting-note`, `etc`
3. **병합 우선**: 기존 파일과 주제가 유사하면 `append`, 아니면 `create`
4. **디렉토리 깊이**: 최대 2~3단계까지만 허용
5. **파일명**: kebab-case 영문

---

## 9. 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| 📌 달아도 반응 없음 | Event Subscriptions 미등록 | Slack App → Event Subscriptions → `reaction_added` 추가 |
| "Channel not targeted" | 채널 ID 불일치 | `SLACK_CONTEXT_CHANNELS`에 정확한 채널 ID 입력 |
| "Already processed" | 중복 이모지 | `_sync/slack-pins.log`에 기록됨. 수동 삭제 시 GitHub에서 해당 라인 제거 |
| 노션 동기화 안 됨 | DB 공유 안 됨 | Integration을 Database에 연결 |
| `target_path` 무시됨 | 필드명 불일치 | Notion 속성명이 정확히 `target_path`인지 확인 |
| EventBridge 미작동 | Lambda 권한 부족 | EventBridge → Lambda invoke 권한 추가 |
