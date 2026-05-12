# deeple-context

> **디플 공통 컨텍스트**를 담는 평행 repo입니다.
> 모든 코드 repo는 `../deeple-context/`를 참조할 수 있습니다.

## 역할

| 저장소 | 역할 |
|--------|------|
| `deeple-context` | **도메인 지식(what)** — 서비스 개요, 도메인 용어, 비즈니스 규칙, 정책, 페르소나 |
| `deeple-skill` | **범용 실행 도구(how)** — 프로세스, 워크플로우, 체크리스트 |
| `GOCHO_BE` | 백엔드 코드 + 기술 문서 (`docs/`) |
| `gocho` | 웹 프론트 코드 + 기술 문서 (`docs/`) |
| `flutter-gocho-app` | Flutter 앱 코드 + 기술 문서 (`docs/`) |

---

## Context vs Skill 경계 (핵심 원칙)

### ✅ Context에 들어가는 것

- **도메인 지식** — "무엇인가" (what)
- **서비스 개요** — 플로우, 기능 설명, 주요 화면
- **비즈니스 규칙** — 환불 조건, 멤버십 혜택, 가격 정책
- **정책 문서** — 환불 정책, 에스컬레이션, 계정 정책
- **CS 페르소나** — 응대 말투, 톤, 이모티콘 기준, 금지어
- **FAQ 답변** — 자주 묻는 질문의 구체적 답변
- **도메인 용어집** — 서비스 특화 용어 정의
- **디자인 시스템** — 색상, 타이포그래피, 컴포넌트 스펙

### ❌ Context에 들어가지 않는 것

- **실행 워크플로우** — "어떻게 한다" (how) (→ `deeple-skill`로 위임)
- **코드 컨벤션** — 네이밍, 아키텍처, 패턴 (→ 코드 레포 `docs/`로 위임)
- **스킬 로직** — Git 커밋 규칙, Jira 티켓 포맷 (→ `deeple-skill`로 위임)
- **MCP 설정법** — 도구 설치/연결 방법 (→ `shared/`에 두되, 실행 로직은 skill)

### 위임 규칙

```
Context는 "무엇(what)"만 담는다.
"어떻게(how)"는 Skill로 위임한다.

예:
- Context: "디맨드 스펙리포트 환불 조건 — 미열관 시 가능, 열관 후 불가"
- Skill: "환불 심사 프로세스 (단계 1~5)"
```

---

## 저장소 구조

```
deeple-context/
├── AGENTS.md              ← 이 파일
├── shared/                ← 공통 조직 지식
│   ├── claude-code-overview.md   ← AI 도구 생태계 개요
│   ├── workspace-guide.md        ← 워크스페이스 구조, Git 규칙, 컨벤션
│   ├── db-guide.md               ← DB Agent & MCP MySQL 사용 가이드
│   ├── mcp-figma-setup.md        ← Figma MCP 설정
│   ├── mcp-mysql-setup.md        ← MySQL MCP 설정
│   └── mcp-puppeteer-setup.md    ← Puppeteer MCP 설정
└── dmand/                 ← 디맨드 서비스 도메인 지식
    ├── design-system.md
    ├── service.md         ← 서비스 개요, 주요 플로우
    ├── domain/
    │   ├── glossary.md    ← 도메인 용어집
    │   └── business-rules.md ← 비즈니스 규칙
    └── cs/
        ├── AGENTS.md      ← CS 스킬 가이드 (전체 흐름)
        ├── persona.md     ← CS 응대 페르소나
        ├── refund-policy.md ← 환불 정책
        ├── account-policy.md ← 계정 정책
        ├── mentoring-policy.md ← 멘토링 중재 정책
        ├── data-curation-policy.md ← 데이터 큐레이션 정책
        ├── faq-guide.md   ← FAQ 가이드
        ├── escalation.md  ← 에스컬레이션 정책
        └── screen-code-db-map.md ← CS 화면→코드→DB 매핑
```

### 구조 확장 규칙

- 새 서비스가 추가되면 `deeple-context/{서비스}/` 하위에 동일한 구조로 생성
- `shared/`는 **조직 전체 공통** 지식만 담는다
- 각 서비스 폴더는 **해당 서비스의 도메인 지식**만 담는다

---

## 참조 규칙

- **로컬 개발**: `../deeple-context/` (형제 폴더, 빠름)
- **CI/새 환경**: `https://github.com/DeepLeHR/deeple-context/` (원격 fallback)
- 각 문서는 **독립적으로 읽혀도 90% 이해 가능**하게 작성
