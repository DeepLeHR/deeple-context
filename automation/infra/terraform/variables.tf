variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "ap-northeast-2"
}

variable "project_name" {
  description = "리소스명 prefix"
  type        = string
  default     = "deeple-context-automation"
}

variable "environment" {
  description = "환경 (prod / dev)"
  type        = string
  default     = "prod"
}

variable "context_repo_owner" {
  description = "deeple-context repo 소유자"
  type        = string
  default     = "DeepLeHR"
}

variable "context_repo_name" {
  description = "deeple-context repo 이름"
  type        = string
  default     = "deeple-context"
}

variable "context_branch" {
  description = "deeple-context 대상 브랜치"
  type        = string
  default     = "main"
}

variable "lambda_timeout" {
  description = "Lambda 타임아웃 (초)"
  type        = number
  default     = 120
}

variable "lambda_memory" {
  description = "Lambda 메모리 (MB)"
  type        = number
  default     = 512
}

variable "log_retention_days" {
  description = "CloudWatch 로그 보관 기간"
  type        = number
  default     = 7
}
