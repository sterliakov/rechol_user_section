resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "rechol-apigateway"
  retention_in_days = 365
}
