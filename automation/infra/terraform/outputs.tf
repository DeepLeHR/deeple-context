output "ecr_repository_url" {
  description = "ECR Repository URL"
  value       = aws_ecr_repository.this.repository_url
}

output "lambda_function_arn" {
  description = "Lambda Function ARN"
  value       = aws_lambda_function.this.arn
}

output "lambda_function_name" {
  description = "Lambda Function Name"
  value       = aws_lambda_function.this.function_name
}

output "secrets_manager_arn" {
  description = "Secrets Manager ARN"
  value       = aws_secretsmanager_secret.this.arn
}

output "eventbridge_rule_arn" {
  description = "EventBridge Rule ARN"
  value       = aws_cloudwatch_event_rule.daily_sync.arn
}

output "github_actions_role_arn" {
  description = "GitHub Actions OIDC Role ARN"
  value       = aws_iam_role.github_actions.arn
}

output "sqs_queue_url" {
  description = "SQS Queue URL"
  value       = aws_sqs_queue.this.url
}
