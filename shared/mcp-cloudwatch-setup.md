# Claude Code·Codex에서 CloudWatch MCP로 로그 보기

**작성 2026-09-01**

Claude Code 또는 Codex(팀원 각자 로컬)에 `awslabs-cloudwatch` MCP 서버를 연결해서, 터미널에
`aws logs ...` 명령을 직접 치지 않고 **대화로 `gocho-api-live`(ECS)·`AIGenerate-live`(Lambda)
등의 로그를 조회·분석**하는 방법.

- 이 MCP로 `/ecs/gocho-api-live`, `/ecs/gocho-api-dev`, `/aws/lambda/AIGenerate-live`, `/aws/lambda/AIGenerate-dev` 로그를 조회할 수 있다. 로그에 사용자 개인정보(이름·전화번호·생년월일 등)가 남아있을 수 있으니 취급에 주의한다(§7).

---

## 1. 사전 준비 (최초 1회)

### 1-1. uv/uvx 설치

```bash
brew install uv
```

`uvx --version`이 나오면 된다. MCP 서버는 `uvx awslabs.cloudwatch-mcp-server@latest`로 매번 최신 버전을 받아 실행한다(별도 설치 불필요).

### 1-2. AWS 자격증명 받기

AWS 액세스 키(`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`)는 AWS Secrets Manager에서 확인한다.

- 슬랙/메일/노션 등에 평문으로 붙여넣지 않는다.
- 시크릿 키는 AWS Secrets Manager의 `dmand/cloudwatch-viewer` 시크릿에서 확인한다.
- 이 문서에는 실제 키 값을 적지 않는다 — 아래 `.mcp.json` 템플릿의 `<...>` 자리에 본인이 받은 값을 채운다.

---

## 2. Claude Code 설정

프로젝트 스코프 MCP 서버는 `~/workspace/deeplehr/.mcp.json` **한 파일에 모여 있다**. GOCHO_BE 안에는 `.mcp.json`이 따로 없다 — Claude Code가 이 상위 파일을 project-scope 설정으로 인식한다.

이 파일은 `~/.gitignore_global`에 의해 **전역 gitignore 처리**돼 있어 어느 리포에도 커밋되지 않는다. 즉 새 팀원의 로컬에는 이 파일이 아예 없을 것이므로 직접 만들어야 한다.

`~/workspace/deeplehr/.mcp.json`:

```json
{
  "mcpServers": {
    "awslabs-cloudwatch": {
      "command": "/Users/<본인계정>/.local/bin/uvx",
      "args": ["awslabs.cloudwatch-mcp-server@latest"],
      "env": {
        "AWS_ACCESS_KEY_ID": "<받은 액세스 키 ID>",
        "AWS_SECRET_ACCESS_KEY": "<받은 시크릿 키>",
        "AWS_REGION": "ap-northeast-2"
      }
    }
  }
}
```

- `command` 경로는 `which uvx`로 본인 환경에 맞게 바꾼다.
- 이미 다른 MCP 서버(jira, github, figma 등)가 이 파일에 있다면 `mcpServers` 객체 안에 `awslabs-cloudwatch` 블록만 추가한다. 기존 블록을 지우지 않는다.

---

## 3. 연결 확인

```bash
claude mcp list
```

`awslabs-cloudwatch: ... - ✔ Connected`가 뜨면 성공. 세부 스코프 확인:

```bash
claude mcp get awslabs-cloudwatch
```

`Scope: Project config (shared via .mcp.json)`가 나와야 한다.

Claude Code 세션 안에서는 다음처럼 물어보면 된다(툴이 자동 로드되지 않으면 `ToolSearch`로 먼저 당겨온다):

> "CloudWatch MCP로 `/ecs/gocho-api-live` 로그 최근 1시간치 ERROR만 찾아줘"

### Codex 연결

Codex는 `~/.codex/config.toml`에 MCP 서버를 등록한다. 액세스 키를 설정 파일에 직접
중복 저장하지 않으려면, 기존 Claude Code 설정을 읽어 실행하는 로컬 런처를 사용한다.

```bash
codex mcp add awslabs-cloudwatch -- ~/.codex/bin/deeple_cloudwatch_mcp.py
codex mcp get awslabs-cloudwatch
```

런처는 `~/workspace/deeplehr/.mcp.json`의 `awslabs-cloudwatch` 명령·환경변수를 읽어서
서버를 실행한다. 따라서 Claude Code 설정의 키를 회전하면 Codex도 같은 키를 자동으로 쓴다.
등록 후에는 새 Codex 세션에서 MCP 도구가 로드된다.

---

## 4. 함정 — 리전(region) 파라미터 필수

**MCP 툴 호출 시 `region: "ap-northeast-2"`를 매번 명시적으로 넣어야 한다.** 넣지 않으면 기본값(`us-east-1`)으로 조회해서 로그 그룹이 안 보인다(`ResourceNotFoundException`). 계정은 맞는데 리전이 달라 "로그 그룹이 없다"는 에러가 나는 함정이다.

- `describe_log_groups` 툴은 `region` 파라미터를 넣어도 원인 불명 에러(`Error executing tool describe_log_groups`)를 내는 경우가 있었다. 이럴 때는 `execute_log_insights_query`에 `region`을 직접 주고 쿼리하면 된다(이쪽은 정상 동작 확인됨). 또는 `aws logs describe-log-groups --region ap-northeast-2`로 대체한다.

---

## 5. 조회 가능한 로그 그룹

| 로그 그룹 | 서비스 |
|---|---|
| `/ecs/gocho-api-live`, `/ecs/gocho-api-dev` | gocho 백엔드(Spring, ECS) — 이 레포 |
| `/aws/lambda/AIGenerate-live`, `/aws/lambda/AIGenerate-dev` | AI 생성(자소서 등) Lambda |

정확한 이름이 기억 안 나면:

```bash
aws logs describe-log-groups --region ap-northeast-2 \
  --log-group-name-prefix "/ecs/gocho-api" --query 'logGroups[].logGroupName' --output text
```

(이 명령은 §1-2의 MCP용 `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` 환경변수가 설정된 상태에서 실행한다.)

---

## 6. 사용 예시

Claude Code 대화창에 자연어로 요청하면 된다. 예:

- "`/ecs/gocho-api-live`에서 지난 1시간 동안 ERROR 로그 찾아줘"
- "`/aws/lambda/AIGenerate-live`에서 오늘 실행된 Lambda 중 30초 넘게 걸린 거 있어?"
- "requestId `0RFM2M00H69N1`로 gocho-api-live랑 AIGenerate-live 양쪽 로그 다 찾아줘"

내부적으로는 `execute_log_insights_query`(CloudWatch Logs Insights 쿼리)나 `describe_log_groups`가 호출된다. 직접 쿼리 문법을 쓰고 싶다면:

```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 50
```

- 쿼리 결과가 크면(대략 5~6만자 이상) 자동으로 로컬 파일에 저장되고 대화창에는 요약만 온다. `| limit 50` 같은 제한을 쿼리에 넣어두면 애초에 덜 걸린다.
- 로그 원문의 `@timestamp`는 **UTC**다. KST로 보려면 +9시간.
- `gocho-api-live`는 nginx 사이드카 액세스 로그와 애플리케이션 로그가 같은 로그 그룹에 섞여 있다(로그 스트림은 `ecs/nginx/*` vs `ecs/spring-api/*`로 구분). 배경은 `GOCHO_BE/docs/infra/cloudwatch-log-cost-reduction.md` §2 참고.

---

## 7. 보안 유의사항

- `~/workspace/deeplehr/.mcp.json`에는 액세스 키가 **평문**으로 들어간다. 전역 gitignore로 커밋은 막혀 있지만, 파일 자체가 크리덴셜이므로 화면 공유·백업·Dropbox 동기화 폴더 등에 노출되지 않게 각자 주의한다.
- 이 키는 서비스 로그를 폭넓게 읽을 수 있어, 로그 메시지에 사용자 개인정보(이름, 전화번호, 생년월일 등)가 그대로 남아있는 경우가 있다(`HttpLoggingFilter`가 요청/응답 바디를 찍는 방식은 `GOCHO_BE/docs/infra/cloudwatch-log-cost-reduction.md` §2~3 참고). 대화 결과를 슬랙/노션 등에 옮길 때 개인정보를 원문 그대로 붙여넣지 않는다.
- 키 로테이션·회수가 필요하면 이 키를 발급한 관리자에게 요청한다.

---

## 8. 안 될 때

| 증상 | 원인 / 조치 |
|---|---|
| `claude mcp list`에 `awslabs-cloudwatch`가 안 보임 | `~/workspace/deeplehr/.mcp.json`이 없거나 JSON 문법 오류. §2 |
| `codex mcp list`에 `awslabs-cloudwatch`가 안 보임 | Codex 등록 명령을 다시 실행한 뒤 새 세션을 연다. §3 |
| `✘ Failed to connect — CONNECTION_CLOSED` | `uvx` 경로가 잘못됐거나 네트워크 문제. `which uvx`로 `command` 값 재확인 |
| 쿼리했는데 로그 그룹이 없다고 나옴(`ResourceNotFoundException`) | `region` 파라미터 누락 → 기본 `us-east-1`로 조회됨. §4 |
| `describe_log_groups` 호출 시 알 수 없는 에러 | 알려진 함정. `execute_log_insights_query`로 대체하거나 CLI로 대체. §4 |
| 결과가 비어 있음 | 권한 문제가 아니라 대개 시간 범위가 짧아서다. `start_time`/`end_time` 넓히기 |
