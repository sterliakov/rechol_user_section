resource "aws_cloudwatch_event_rule" "warmup" {
  name                = "rechol-backend-warmup-event"
  schedule_expression = "rate(5 minutes)"
}
resource "aws_cloudwatch_event_target" "warmup" {
  rule = aws_cloudwatch_event_rule.warmup.name
  arn  = aws_lambda_alias.backend_stable.arn
  input = jsonencode({
    action = "PING"
  })
}
