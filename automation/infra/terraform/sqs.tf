resource "aws_sqs_queue" "this" {
  name                       = "${var.project_name}-queue"
  visibility_timeout_seconds = 60  # Lambda timeout보다 길게
  message_retention_seconds  = 86400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })
}

resource "aws_sqs_queue" "dlq" {
  name                       = "${var.project_name}-dlq"
  message_retention_seconds  = 1209600  # 14일
}

resource "aws_lambda_event_source_mapping" "sqs" {
  event_source_arn = aws_sqs_queue.this.arn
  function_name    = aws_lambda_function.this.arn
  batch_size       = 1  # 1건씩 처리 (순서 보장 + 오류 격리)

  depends_on = [aws_iam_role_policy_attachment.lambda_sqs]
}

resource "aws_lambda_permission" "allow_sqs" {
  statement_id  = "AllowSQSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_sqs_queue.this.arn
}
