# 디플 AI 도구 생태계

> 회사 전 직원(개발자, 디자이너, 기획자, HR, PO 등)이 공통으로 사용하는 AI 스킬 및 컨텍스트 저장소 개요.

---

## 저장소 구조

```
deeplehr/
├── deeple-context/        ← 공통 컨텍스트 (도메인 지식, 정책, 가이드)
│   ├── shared/            ← 조직 공통 지식
│   └── dmand/             ← 서비스별 도메인 지식
├── deeple-skill/          ← 전사 공용 스킬 아카이브 (실행 도구)
│   └── .ai/skills/
│       ├── git/           ← Git 워크플로우
│       ├── pm/            ← PM 워크플로우
│       ├── design/        ← 디자인 워크플로우
│       ├── qa/            ← QA 워크플로우
│       ├── cs/            ← CS 워크플로우
│       ├── dev/           ← 개발 보조
│       └── util/          ← 유틸리티
├── deeple-tools/          ← 자동화/모니터링/업로더 등 도구
├── GOCHO_BE/              ← 백엔드 코드 + 기술 문서
├── gocho/                 ← 웹 프론트 코드 + 기술 문서
└── flutter-gocho-app/     ← Flutter 앱 코드 + 기술 문서
```

---

## 스킬 아키텍처

### 핵심 원칙

| | Skill | Context |
|---|---|---|
| **역할** | 범용 매뉴얼 (프로세스, 포맷, 워크플로우) | 도메인 지식 (정책, 규칙, 페르소나) |
| **위치** | `deeple-skill/.ai/skills/{카테고리}/` | `deeple-context/{서비스}/` |
| **예시** | 버그 분석 포맷, 환불 심사 프로세스, Git 커밋 규칙 | 디맨드 환불 정책, 디맨드 CS 톤&보이스 |

```
사용자 문의 → Context (도메인 맥락) + Skill (범용 프로세스) → 처리
```

### Skill = 범용 (서비스 무관)

어떤 서비스에서든 재사용할 수 있는 **프로세스, 포맷, 워크플로우**를 정의합니다.

- 버그 분석 Jira 티켓 포맷 → `deeple-skill/.ai/skills/cs/cs-bug-analyze/`
- 환불 심사 프로세스 → `deeple-skill/.ai/skills/cs/cs-refund-check/`
- Git 커밋 규칙 → `deeple-skill/.ai/skills/git/commit/`
- Figma → 코드 퍼블리싱 → `deeple-skill/.ai/skills/design/publisher/`

### Context = 서비스/도메인 특화

해당 서비스의 **도메인 맥락, 정책, 톤**을 담습니다. Skill은 Context 없이 실행되지 않습니다.

- 디맨드 환불 정책 (스펙리포트/멘토링) → `deeple-context/dmand/cs/refund-policy.md`
- 디맨드 CS 톤&보이스 (페르소나) → `deeple-context/dmand/cs/persona.md`
- 디맨드 백엔드 구현 컨벤션 → `GOCHO_BE/docs/backend-patterns.md`

### 새 기능 추가 시 판단 기준

```
"다른 서비스에서도 쓸 수 있는가?"
  → Yes: Skill로 만든다 (deeple-skill/.ai/skills/{카테고리}/)
  → No:  Context 문서에 포함한다 (deeple-context/{서비스}/)

"상세 매뉴얼이 필요한가?"
  → Yes: Skill로 만든다
  → No:  Context 문서 단독으로 충분
```

---

## 스킬 카테고리

| 그룹 | 스킬 | 설명 | 대상 |
|------|------|------|------|
| **git/** | commit, branch, pr, push | Git 워크플로우 자동화 | 전 직원 |
| **cs/** | cs-router, cs-reply-draft, cs-refund-check, cs-bug-analyze, cs-bug-handler, cs-code-debug | CS 프로세스 & 포맷 | CS / 기획자 |
| **qa/** | spec-web, spec-app, design-web, design-app, edge, pipeline, web-qa | QA 테스트 & 파이프라인 | QA / 개발자 |
| **design/** | figma-flow-plugin, figma-ux-review, figma-wireframe-flow, publisher | Figma 디자인 도구 & 퍼블리싱 | 디자이너 / 개발자 |
| **pm/** | jira, func-spec | Jira 티켓 관리, 기능 명세서 | 기획자 / PM |
| **dev/** | review, debug, db-query, api-integration, architect, backend-patterns, context-manager, security-review, backend-dev, app-dev, web-frontend-dev, uploader | 개발 도구 & 아키텍처 | 개발자 |
| **util/** | usage | 세션 사용량 확인 | 전 직원 |

---

## MCP 서버

| MCP 서버 | 용도 | 설정 가이드 |
|----------|------|------------|
| MySQL MCP | DB 조회 / 스키마 분석 | `deeple-context/shared/mcp-mysql-setup.md` |
| Figma MCP | 디자인 스펙 참조 | `deeple-context/shared/mcp-figma-setup.md` |
| Puppeteer MCP | 브라우저 자동화 / 스크린샷 | `deeple-context/shared/mcp-puppeteer-setup.md` |
