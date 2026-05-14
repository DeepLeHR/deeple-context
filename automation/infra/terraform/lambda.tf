resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${var.project_name}"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "this" {
  function_name = var.project_name
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.this.repository_url}:latest"

  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory

  environment {
    variables = {
      CONTEXT_REPO_OWNER   = var.context_repo_owner
      CONTEXT_REPO_NAME    = var.context_repo_name
      CONTEXT_BRANCH       = var.context_branch
      SQS_QUEUE_URL        = aws_sqs_queue.this.url
      SECRETS_MANAGER_NAME = aws_secretsmanager_secret.this.name
      AWS_REGION           = var.aws_region
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.this,
    aws_iam_role_policy_attachment.lambda_basic,
  ]

  lifecycle {
    ignore_changes = [image_uri]  # GitHub Actions에서 별도 업데이트
  }
}

# Lambda 함수 URL (선택 — Slack Event API용)
# resource "aws_lambda_function_url" "this" {
#   function_name      = aws_lambda_function.this.function_name
#   authorization_type = "NONE"
# }
