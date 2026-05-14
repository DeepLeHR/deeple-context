# Terraform 배포 가이드

> Docker + ECR + Lambda + EventBridge를 Terraform으로 선언적으로 관리합니다.

## 아키텍처

```
GitHub Actions (OIDC)
  ├─ docker build → ECR push
  ├─ terraform apply
  └─ lambda update-function-code

AWS
  ├─ ECR (deeple-context-automation)
  ├─ Lambda (deeple-context-automation) ← Docker image
  ├─ EventBridge (cron 00:00 KST) → Lambda
  ├─ SQS (Worker queue) → Lambda
  ├─ CloudWatch Logs
  ├─ Secrets Manager (API keys)
  └─ IAM (Lambda role + GitHub Actions OIDC role)
```

---

## 1. 사전 준비

### 1.1 로컬 도구 설치
```bash
brew install terraform awscli docker
```

### 1.2 AWS 인증
```bash
aws configure
# Access Key / Secret Key 입력
```

### 1.3 Terraform state용 S3 버킷 생성 (한 번만)
```bash
aws s3 mb s3://deeple-terraform-state --region ap-northeast-2
aws s3api put-bucket-versioning \
  --bucket deeple-terraform-state \
  --versioning-configuration Status=Enabled
```

> ⚠️ **반드시 S3 backend를 활성화하세요.** 팀원 간 상태 공유와 drift 방지를 위해 필수입니다.

---

## 2. 초기 인프라 배포 (Local)

### 2.1 backend 활성화
`automation/infra/terraform/main.tf`의 S3 backend 주석을 해제하거나, `automation/infra/terraform/backend.tf`를 생성:

```hcl
terraform {
  backend "s3" {
    bucket         = "deeple-terraform-state"
    key            = "deeple-context-automation/terraform.tfstate"
    region         = "ap-northeast-2"
    encrypt        = true
    dynamodb_table = "deeple-terraform-locks"  # optional: state locking
  }
}
```

### 2.2 초기화 및 배포
```bash
cd automation/infra/terraform

# 첫 init은 local backend로 진행
terraform init

# plan 확인
terraform plan

# apply (ECR, Lambda, IAM, EventBridge, Secrets Manager, SQS 생성)
terraform apply
```

### 2.3 출력값 확인
```bash
terraform output
# ecr_repository_url
# lambda_function_arn
# github_actions_role_arn  ← GitHub Secrets에 등록할 값
```

---

## 3. Secrets Manager에 실제 값 입력

Terraform으로 생성된 Secrets Manager에 실제 API 키/토큰을 입력합니다.

```bash
aws secretsmanager put-secret-value \
  --secret-id deeple-context-automation/prod \
  --secret-string '{
    "ANTHROPIC_API_KEY": "sk-xxx",
    "GITHUB_TOKEN": "ghp-xxx",
    "SLACK_BOT_TOKEN": "xoxb-xxx",
    "SLACK_CONTEXT_CHANNELS": "C123,C456",
    "NOTION_TOKEN": "secret_xxx",
    "NOTION_PLANNING_DB_ID": "1234-5678-..."
  }'
```

> Lambda 함수도 환경변수로 설정 가능하지만, 민감한 값은 Secrets Manager가 권장됩니다.

---

## 4. GitHub Actions 연동

### 4.1 GitHub Secrets 설정
Repository → Settings → Secrets and variables → Actions → New repository secret

| Secret Name | Value |
|-------------|-------|
| `AWS_DEPLOY_ROLE_ARN` | `terraform output github_actions_role_arn` 결과 |

### 4.2 첫 Docker 이미지 빌드 & 푸시
GitHub Actions가 자동으로 처리하지만, 첫 이미지는 수동으로 push해야 Lambda가 초기화됩니다:

```bash
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.ap-northeast-2.amazonaws.com

cd automation
docker build -t deeple-context-automation .
docker tag deeple-context-automation:latest $(terraform output -raw ecr_repository_url):latest
docker push $(terraform output -raw ecr_repository_url):latest

# Lambda 이미지 업데이트
aws lambda update-function-code \
  --function-name deeple-context-automation \
  --image-uri $(terraform output -raw ecr_repository_url):latest
```

### 4.3 이후 배포
`main` 브랜치에 push하면 GitHub Actions가 자동으로:
1. Docker build → ECR push
2. Terraform apply
3. Lambda update-function-code

---

## 5. Slack Event API 엔드포인트 설정

Lambda가 배포된 후 **API Gateway** 또는 **Lambda Function URL** 엔드포인트를 Slack App의 Request URL에 등록합니다.

### 5.1 API Gateway (권장)
API Gateway v2 → HTTP API → Lambda integration 생성 후, 엔드포인트를 Slack에 등록.

### 5.2 Lambda Function URL (간단)
```bash
aws lambda create-function-url-config \
  --function-name deeple-context-automation \
  --auth-type NONE
```
생성된 URL을 Slack App → Event Subscriptions → Request URL에 입력.

> ⚠️ 현재 Terraform에는 Lambda Function URL 리소스가 없습니다. `lambda.tf`의 주석을 해제하거나 API Gateway를 별도로 생성하세요.

---

## 6. 유용한 명령어

```bash
# 로그 확인
aws logs tail /aws/lambda/deeple-context-automation --follow

# Lambda 수동 invoke (테스트)
aws lambda invoke \
  --function-name deeple-context-automation \
  --payload '{"source":"aws.events"}' \
  response.json && cat response.json

# Terraform destroy (전체 삭제)
cd automation/infra/terraform
terraform destroy
```

---

## 7. 파일 구조

```
deeple-context/
├── automation/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   ├── .github/
│   │   └── workflows/
│   │       └── automation-deploy.yml
│   ├── infra/
│   │   └── terraform/
│   │       ├── main.tf
│   │       ├── backend.tf          ← S3 backend (생성 필요)
│   │       ├── variables.tf
│   │       ├── outputs.tf
│   │       ├── ecr.tf
│   │       ├── iam.tf
│   │       ├── lambda.tf
│   │       ├── eventbridge.tf
│   │       ├── sqs.tf
│   │       └── secrets.tf
│   ├── src/
│   │   ├── lambda_function.py
│   │   ├── context_analyzer.py
│   │   ├── context_git.py
│   │   ├── context_save_handler.py
│   │   ├── secrets_loader.py
│   │   ├── slack/
│   │   │   ├── event_processor.py
│   │   │   ├── extractor.py
│   │   │   └── sender.py
│   │   └── notion/
│   │       ├── client.py
│   │       ├── converter.py
│   │       └── db_sync.py
│   └── docs/
│       ├── context-automation-setup.md
│       ├── terraform-setup.md
│       └── setup-checklist.md
```
