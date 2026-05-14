resource "aws_secretsmanager_secret" "this" {
  name        = "${var.project_name}/${var.environment}"
  description = "Slack Bot Lambda 환경변수 (API 키, 토큰 등)"

  recovery_window_in_days = 7
}

# 초기 더미 값. 실제 값은 AWS 콘솔이나 CLI로 업데이트
resource "aws_secretsmanager_secret_version" "initial" {
  secret_id = aws_secretsmanager_secret.this.id
  secret_string = jsonencode({
    ANTHROPIC_API_KEY     = "sk-ant-placeholder"
    GITHUB_TOKEN          = "ghp-placeholder"
    SLACK_BOT_TOKEN       = "xoxb-placeholder"
    SLACK_CONTEXT_CHANNELS = ""
    NOTION_TOKEN          = "secret-placeholder"
    NOTION_PLANNING_DB_ID = ""
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}
