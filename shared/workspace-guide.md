# Project Structure

> 루트 디렉토리: `~/workspace/deeplehr/`

```
~/workspace/deeplehr/
├── GOCHO_BE/              # Backend (Spring Boot / Java)
├── gocho/                 # Frontend (Web)
├── flutter-gocho-app/     # App (Flutter)
├── deeple-context/        # 공통 컨텍스트 (도메인 지식, 정책)
└── deeple-skill/          # 전사 공용 스킬 아카이브 (실행 도구)
```

---

## 스킬 및 컨텍스트 레포 구조

```
deeple-skill/
└── .ai/skills/
    ├── git/               # Git 워크플로우
    ├── qa/                # QA 테스트
    ├── design/            # 디자인 도구
    ├── pm/                # 프로젝트 관리
    ├── cs/                # CS 워크플로우
    ├── dev/               # 개발 도구
    └── util/              # 유틸리티

deeple-context/
├── shared/                # 조직 공통 지식
│   ├── claude-code-overview.md
│   ├── workspace-guide.md
│   ├── db-guide.md
│   └── mcp-*.md
└── dmand/                 # 서비스별 도메인 지식
    ├── service.md
    ├── design-system.md
    ├── domain/
    └── cs/
```

---

## 작업 경로 규칙

- **Backend** → `~/workspace/deeplehr/GOCHO_BE/` 기준으로 파일 탐색 및 수정
- **Frontend** → `~/workspace/deeplehr/gocho/` 기준으로 파일 탐색 및 수정
- **App** → `~/workspace/deeplehr/flutter-gocho-app/` 기준으로 파일 탐색 및 수정
- **Skill/Context 관리** → `~/workspace/deeplehr/deeple-skill/` 또는 `~/workspace/deeplehr/deeple-context/` 기준

작업 대상 레포가 명확하지 않으면 사용자에게 확인 후 진행한다.

---

## Skill vs Context 가이드

| | Skill | Context |
|---|---|---|
| **역할** | 범용 워크플로우 (how) | 도메인 지식 (what) |
| **위치** | `deeple-skill/.ai/skills/` | `deeple-context/{서비스}/` |
| **예시** | `/git/commit`, `/cs/refund-check`, `/qa/spec-web` | 환불 정책, CS 페르소나, 도메인 용어집 |

Skill은 **어떤 프로젝트에서든 재사용 가능한 실행 프로세스**를 정의합니다.
Context는 **특정 서비스의 도메인 규칙과 정책**을 담습니다.

---

## Git & Branch 규칙

### 브랜치 작업 순서 (MUST)

1. **작업 시작 전 반드시 `dev` 최신화**
   ```bash
   git checkout dev
   git pull origin dev
   ```
2. **최신화된 `dev` 기반으로 브랜치 생성**
   ```bash
   git checkout -b feat/DL-{ticket}-{description}
   ```
3. **PR 타겟 브랜치는 항상 `dev`**

### 브랜치 네이밍

- `feat/DL-{ticket}-{short-desc}` — 신규 기능
- `fix/DL-{ticket}-{short-desc}` — 버그 수정
- `hotfix/DL-{ticket}-{short-desc}` — 긴급 수정

### MUST NOT

- `dev` 최신화 없이 브랜치를 절대 따지 말 것 → 충돌 원인
- `main` / `master` 브랜치로 직접 PR 금지

---

# Conventions

> Java 파일 작업 시 항상 적용되는 코드 철학, 네이밍, OOP 설계, Java 스타일 가이드

## MUST

- Code MUST be self-documenting; readable without comments
- Comments MUST explain "why", never "what"
- TODO, FIXME, NOTE MUST include owner and timeline: `// TODO: 2025-06 Refactor (owner: jinho)`
- Classes MUST have a single responsibility (SRP)
- Names MUST read like English: calculateTotalPrice, fetchUserProfile, isEmailVerified
- Use PascalCase for classes: OrderService, UserProfile
- Use camelCase for methods and variables: calculateTotalAmount, userName
- Use UPPER_SNAKE_CASE for constants: MAX_RETRY_COUNT
- Boolean names MUST use is/has with affirmative form: isVerified, hasPermission
- API path MUST follow: `/api/v{version}/{service}/{resource}`
- One method MUST perform exactly one responsibility
- Use early return to simplify conditionals
- Consolidate null checks; throw a single exception (e.g. NullOrBlankException)

## MUST NOT

- NEVER use abbreviations (btn, svc, usr). Exception: JD, Auth, AI
- NEVER use wildcard imports (`import x.*`). Always use explicit imports
- NEVER put multiple responsibilities in one class
- NEVER write comments that describe what code does (the code should show that)
- NEVER use magic numbers. Define constants instead
- NEVER use negative Boolean names (isUnverified). Use affirmative (isVerified)
- NEVER put multiple responsibilities in one method
- NEVER swallow exceptions in empty catch blocks

## SHOULD

- Abstract common logic for reuse
- Follow SOLID principles

## CRUD Methods

- save, saveAll / findById, findByEmail / findAllByStatus, findAll / update, updatePassword / deleteById

## Exception Naming Convention

- `404 NOT_FOUND` → `XxxNotFoundException`
- `400 INVALID_FORMAT` → `InvalidXxxFormatException`
- `400 ALREADY_EXISTS` → `XxxAlreadyExistsException`
- `400 NULL_OR_BLANK` → `NullOrBlankException`
- `400 INFORMATION_MISMATCH` → `XxxMismatchException`
- `401 UNAUTHORIZED` → `ExpiredTokenException`
- Consolidate null checks into a single `NullOrBlankException`; never throw per-field nulls

## Layer Responsibilities

- Controller: receive request, delegate to service — no business logic
- DTO: structure + validation annotations only (`@NotBlank`, `@Email`, `@Size`) — no logic
- Assembler / Extension Function: DTO → Entity conversion (`fun XxxRequestDto.toEntity()`)
- Entity: domain integrity validation via static factory (`companion object { fun of(...) }`)

## Test Naming Convention

- Method format: `given_상황_when_행동_then_결과`
- Example: `givenExpiredToken_whenVerify_thenThrowException`
- Cover: happy path, edge cases, exception cases per method

## Architecture

- SRP: Separate UserValidator, UserService, UserRepository
- OCP: Extend via Strategy pattern
- DIP: Depend on interfaces, inject implementations

## Code Review Checklist

Before approving: readability, OOP design, naming consistency, reusability, performance. Understandable without comments? SRP satisfied?

## 파일 삭제 규칙

- 절대 `rm`, `rmdir`, `unlink` 사용 금지
- 파일 삭제 시 반드시 `trash` 명령어 사용 (복구 가능)
- `rm`을 폰백으로 절대 사용하지 말 것

## 파일 이동/이름변경 규칙

- `mv` 사용 시 반드시 `-n` 플래그 사용
- 대상 파일이 이미 존재하면 덮어쓰지 않고 중단
