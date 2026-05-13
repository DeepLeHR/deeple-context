# 자정 KST (UTC 15:00)에 실행
resource "aws_cloudwatch_event_rule" "daily_sync" {
  name                = "${var.project_name}-daily-sync"
  description         = "Context 자동 동기화 — 매일 자정 KST"
  schedule_expression = "cron(0 15 * * ? *)"
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.daily_sync.name
  target_id = "LambdaTarget"
  arn       = aws_lambda_function.this.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_sync.arn
}
