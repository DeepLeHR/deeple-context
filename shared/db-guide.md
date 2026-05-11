# DB Agent & Skill 사용 가이드

## 구성 요소

| 파일 | 역할 |
|------|------|
| `deeple-skill/.ai/skills/dev/db-query/SKILL.md` | DB 키워드 감지 → 직접 처리 or mysql-analyst 위임 |
| `deeple-skill/.ai/skills/dev/mysql-analyst/SKILL.md` | 복잡한 쿼리·분석 전담 |

---

## 연결 정보

- **Database**: `GD_dev`
- **접속**: MCP MySQL (`mcp__mysql_db__mysql_query`) — **READ-ONLY**
- **MCP 설정 파일**: 레포 루트 `.mcp.json` (팀 공유, 비번은 env로 주입)

---

## MCP 연결 설정 (팀원 필수)

레포 루트의 `.mcp.json`은 공용 설정이며 자격증명은 **각자 셸 환경변수**로 주입한다.

### 1. 환경변수 설정 (`~/.zshrc` 또는 `~/.bashrc`)

```bash
export MYSQL_USER="본인_계정"        # 예: read_only_claude_dev
export MYSQL_PASS="본인_비번"
```

> Claude 전용 read 계정(`claude_user`, `read_only_claude_dev`) 등 개인에게 발급된 계정을 사용한다.

### 2. 커넥션 정책 (공용 `.mcp.json`에 이미 반영)

| 환경변수 | 값 | 목적 |
|---------|---|-----|
| `MYSQL_CONNECT_TIMEOUT` | `5000` | 접속 타임아웃 5초 |
| `MYSQL_QUEUE_LIMIT` | `5` | 대기열 5개로 제한 |

> `@benborla29/mcp-server-mysql`은 `enableKeepAlive: true`가 하드코딩이라 idle 커넥션을 계속 붙잡는다. DB 쪽에서도 `MAX_USER_CONNECTIONS` 제한 + 장기 세션 KILL 이벤트를 걸어둔다.

### 3. 세션 정리 (DB 관리자 작업)

```sql
ALTER USER 'claude_user'@'%'          WITH MAX_USER_CONNECTIONS 3;
ALTER USER 'read_only_claude_dev'@'%' WITH MAX_USER_CONNECTIONS 3;
FLUSH PRIVILEGES;

-- 60초 넘는 쿼리 자동 KILL 이벤트는 `deeple-context/shared/db-guide.md` 히스토리 참조
```

---

## 사용 방법

### 1. Skill 자동 트리거

아래 키워드가 포함되면 `db-query` skill이 자동으로 활성화됩니다.

> `DB`, `쿼리`, `query`, `테이블`, `스키마`, `schema`, `데이터 조회`, `데이터베이스`, `mysql`, `조회해줘`, `몇 건`, `통계`, `집계`

```
# 단순 조회 → skill이 직접 처리
"user 테이블 최근 가입자 10명 보여줘"
"jd 테이블 몇 건이야?"
"company 테이블 구조 알려줘"
"spec 데이터 조회해줘"
```

```
# 복잡한 분석 → skill이 mysql-analyst에 위임
"월별 신규 가입자 추이랑 전환율 분석해줘"
"jd_applicant랑 user 조인해서 지원 통계 뽑아줘"
"spec_report 정합성 검증해줘"
"이번 달 캠페인별 전환율 집계해줘"
```

---

### 2. mysql-analyst 직접 지목

복잡한 분석을 바로 Agent에 넘기고 싶을 때:

```
"mysql-analyst한테 맡겨서 이번 달 캠페인 통계 분석해줘"
"mysql-analyst로 spec ~ jd 간 정합성 검증해줘"
```

---

### 3. skill vs agent 판단 기준

| 작업 유형 | 처리 주체 |
|----------|----------|
| 단순 SELECT (단일 테이블, 조건 1~2개) | skill 직접 처리 |
| 스키마 확인 (`DESCRIBE`, `SHOW TABLES`) | skill 직접 처리 |
| 멀티 테이블 JOIN / 서브쿼리 | mysql-analyst |
| 인덱스·실행계획 분석 (`EXPLAIN`) | mysql-analyst |
| 데이터 정합성 검증 | mysql-analyst |
| 운영 리포트·복잡한 집계 | mysql-analyst |

---

## 제약사항

| 항목 | 내용 |
|------|------|
| 권한 | SELECT 전용. INSERT / UPDATE / DELETE / DDL 불가 |
| 결과 건수 | 기본 100건 LIMIT. 1,000건 이상은 실행 전 확인 |
| 민감 데이터 | 비밀번호·토큰 컬럼 자동 마스킹 (`****`) |
| soft delete | `deleted_at` 컬럼이 있는 테이블만 `IS NULL` 조건 포함 |

---

## 주요 테이블 도메인 요약

| 도메인 | 주요 테이블 |
|--------|------------|
| 사용자 | `user`, `user_role`, `user_policy`, `auth_crt` |
| 기업/매니저 | `company`, `manager`, `partnership` |
| 채용공고 | `jd`, `jd_applicant`, `jd_application`, `jd_bookmark` |
| 이력서 | `resume`, `resume_career`, `resume_education` |
| 스펙 | `spec`, `spec_report`, `spec_career`, `spec_event_log` |
| 멘토링 | `mentor`, `mentoring`, `mentoring_review` |
| 콘텐츠 | `blog_post`, `feed`, `qna`, `feedback`, `notice` |
| 결제/상품 | `order`, `plan`, `subscription`, `coupon`, `credit_transaction` |
| 통계 | `banner_statistics`, `campaign_statistics`, `spec_analytics_daily` |

> 전체 테이블 목록은 `deeple-skill/.ai/skills/dev/mysql-analyst/SKILL.md` 참고

---

## 자주 쓰는 쿼리 예시

### 테이블 전체 건수 확인
```
"user 테이블 총 몇 명이야?"
"jd 테이블 활성 공고 몇 건?"
```

### 기간별 통계
```
"이번 달 신규 가입자 일별로 보여줘"
"3월 jd 지원 건수 집계해줘"
```

### 스키마 파악
```
"spec 테이블 구조 알려줘"
"jd_application 컬럼 목록 보여줘"
```

### 데이터 정합성
```
"jd_applicant 중 user가 없는 건 있어?"
"spec_report_item 중 spec이 없는 고아 데이터 확인해줘"
```

### 실행계획 분석
```
"user 테이블 email 조회 쿼리 성능 분석해줘"
"jd 공고 목록 쿼리 인덱스 확인해줘"
```
