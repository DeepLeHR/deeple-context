# Context Automation 세팅 체크리스트

> deeple-context Slack/Notion 자동화 시스템을 처음부터 끝까지 세팅하는 체크리스트입니다.  
> 모든 항목을 순서대로 진행하세요.

---

## Phase 1: 사전 준비 (Key 발급)

### 1. Anthropic (Claude API)
- [ ] [console.anthropic.com](https://console.anthropic.com) 로그인
- [ ] API Key 생성 → 복사해 둠 (`ANTHROPIC_API_KEY`)

### 2. Slack App
- [ ] [api.slack.com/apps](https://api.slack.com/apps) → Create New App → From scratch
- [ ] **OAuth & Permissions** → Bot Token Scopes 추가:
  - `commands`
  - `chat:write`
  - `reactions:read`
  - `channels:history`
  - `groups:history`
  - `im:history`
  - `mpim:history`
- [ ] **Event Subscriptions** → Enable → `reaction_added` 구독
- [ ] **Slash Commands** → Create New Command:
  - Command: `/context-save`
  - Request URL: (Phase 4 이후 Lambda 엔드포인트 입력)
- [ ] **Install to Workspace** → Bot User OAuth Token 복사 (`SLACK_BOT_TOKEN`)
- [ ] 대상 채널의 채널 ID 확인 → 복사 (`SLACK_CONTEXT_CHANNELS`, 쉼표 구분)

### 3. Notion Integration
- [ ] [www.notion.so/my-integrations](https://www.notion.so/my-integrations) → New integration
- [ ] 이름: `Context Automation` → Internal Integration Token 복사 (`NOTION_TOKEN`)
- [ ] 동기화할 Database 페이지 → `⋯` → `Add connections` → `Context Automation` 선택
- [ ] Database에 아래 속성 추가:
  | 속성명 | 타입 |
  |--------|------|
  | `sync_to_context` | Checkbox |
  | `target_path` | Text |
  | `synced_at` | Date |
- [ ] Database 페이지 URL에서 DB ID 추출 (`NOTION_PLANNING_DB_ID`)

### 4. GitHub Token
- [ ] GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
- [ ] `repo` scope 선택 → 토큰 복사 (`GITHUB_TOKEN`)

### 5. AWS 계정
- [ ] AWS CLI 설치 및 인증 (`aws configure`)
- [ ] Terraform 설치 (`brew install terraform`)
- [ ] Docker 설치 (로컬 빌드용)

---

## Phase 2: Terraform 인프라 배포

### 6. S3 Backend 버킷 생성
```bash
aws s3 mb s3://deeple-terraform-state --region ap-northeast-2
aws s3api put-bucket-versioning \
  --bucket deeple-terraform-state \
  --versioning-configuration Status=Enabled
```
- [ ] 버킷 생성 완료

### 7. Terraform 초기화 및 배포
```bash
cd automation/infra/terraform

# S3 backend 활성화 (main.tf 주석 해제 또는 backend.tf 생성)
terraform init
terraform plan
terraform apply
```
- [ ] `terraform apply` 성공
- [ ] 출력값 확인 (`terraform output`):
  - `ecr_repository_url`
  - `lambda_function_arn`
  - `github_actions_role_arn` ← **GitHub Secret에 필요**

### 8. Secrets Manager에 실제 값 입력
```bash
aws secretsmanager put-secret-value \
  --secret-id deeple-context-automation/prod \
  --secret-string '{
    "ANTHROPIC_API_KEY": "sk-ant-xxxxx",
    "GITHUB_TOKEN": "ghp-xxxxx",
    "SLACK_BOT_TOKEN": "xoxb-xxxxx",
    "SLACK_CONTEXT_CHANNELS": "C1234567890,C0987654321",
    "NOTION_TOKEN": "secret_xxxxx",
    "NOTION_PLANNING_DB_ID": "12345678-1234-1234-1234-123456789abc"
  }'
```
- [ ] Secrets Manager 값 입력 완료

---

## Phase 3: 첫 Docker 이미지 배포

### 9. 수동 빌드 & 푸시 (초기 1회)
```bash
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.ap-northeast-2.amazonaws.com

cd automation
docker build -t deeple-context-automation .
docker tag deeple-context-automation:latest \
  $(terraform -chdir=infra/terraform output -raw ecr_repository_url):latest
docker push $(terraform -chdir=infra/terraform output -raw ecr_repository_url):latest

# Lambda 코드 업데이트
aws lambda update-function-code \
  --function-name deeple-context-automation \
  --image-uri $(terraform -chdir=infra/terraform output -raw ecr_repository_url):latest
```
- [ ] ECR push 성공
- [ ] Lambda `update-function-code` 성공

---

## Phase 4: Slack / Notion 연동

### 10. Lambda 엔드포인트 생성
- [ ] API Gateway v2 HTTP API 생성 → Lambda integration
- [ ] 또는 Lambda Function URL 생성:
  ```bash
  aws lambda create-function-url-config \
    --function-name deeple-context-automation \
    --auth-type NONE
  ```
- [ ] 엔드포인트 URL 복사

### 11. Slack Event API 등록
- [ ] Slack App → Event Subscriptions → Request URL에 Lambda 엔드포인트 입력
- [ ] `url_verification` challenge 통과 확인
- [ ] `reaction_added` 이벤트 활성화 확인
- [ ] Slash Command `/context-save`의 Request URL도 동일하게 입력

### 12. 검증
- [ ] **Slack 테스트**: 지정된 채널에 메시지 작성 → 📌 이모지 추가 → 10초 내 `_sync/slack-pins.log`에 기록되는지 확인
- [ ] **Notion 테스트**: 기획 DB 페이지 하나를 만들고 `sync_to_context` 체크 → Lambda 수동 실행:
  ```bash
  aws lambda invoke \
    --function-name deeple-context-automation \
    --payload '{"source":"aws.events"}' \
    response.json && cat response.json
  ```
- [ ] **Slash Command 테스트**: 슬랙에 `/context-save https://www.notion.so/...` 입력 → PR 생성 확인

---

## Phase 5: GitHub Actions 자동화

### 13. GitHub Secrets 설정
- [ ] `deeple-context` repo → Settings → Secrets and variables → Actions
- [ ] `AWS_DEPLOY_ROLE_ARN` 추가 (값 = `terraform output github_actions_role_arn`)

### 14. 자동 배포 테스트
- [ ] `automation/` 내 임의 파일 수정 → `main` 브랜치 push
- [ ] GitHub Actions 워크플로우 성공 확인
- [ ] ECR에 새 이미지 태그 생성 확인
- [ ] Lambda 이미지 업데이트 확인

---

## 🚨 자주 놓치는 것

| 항목 | 확인 방법 |
|------|----------|
| **S3 backend 미활성화** | `terraform show` → local state인지 확인 |
| **Secrets Manager 이름 오타** | AWS 콘솔 → Secrets Manager → `deeple-context-automation/prod` 확인 |
| **OIDC repo 이름 불일치** | `iam.tf`의 `token.actions.githubusercontent.com:sub` 값 확인 |
| **Lambda 엔드포인트 없음** | Slack Request URL 등록 안 하면 이벤트 수신 불가 |
| **Notion Integration 미공유** | Database 페이지 `Add connections`에 `Context Automation` 있는지 확인 |
| **Private 채널 필터** | DM/Private 채널은 보안상 무시됨 (의도된 동작) |

---

## 환경변수/Key 요약

| Key / 변수 | 보관 위치 | 용도 |
|-----------|----------|------|
| `ANTHROPIC_API_KEY` | Secrets Manager | Claude AI 분석 |
| `GITHUB_TOKEN` | Secrets Manager | GitHub API (PR 생성, 파일 쓰기) |
| `SLACK_BOT_TOKEN` | Secrets Manager | Slack API (메시지 읽기, 이모지 감지) |
| `SLACK_CONTEXT_CHANNELS` | Secrets Manager | 📌 허용 채널 ID 목록 |
| `NOTION_TOKEN` | Secrets Manager | Notion API |
| `NOTION_PLANNING_DB_ID` | Secrets Manager | 동기화 대상 DB ID |
| `AWS_DEPLOY_ROLE_ARN` | GitHub Secrets | GitHub Actions → AWS OIDC 인증 |

---

> **모든 체크가 완료되면 자동화 시스템이 정상 동작합니다!**  
> 문제가 발생하면 `aws logs tail /aws/lambda/deeple-context-automation --follow`로 로그를 확인하세요.
