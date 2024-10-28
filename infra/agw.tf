resource "aws_apigatewayv2_stage" "main" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      httpMethod      = "$context.httpMethod"
      protocol        = "$context.protocol"
      path            = "$context.path"
      status          = "$context.status"
      ip              = "$context.identity.sourceIp"
      requestId       = "$context.requestId"
      requestTime     = "$context.requestTime"
      responseLength  = "$context.responseLength"
      routeKey        = "$context.routeKey"
      latency         = "$context.integration.latency"
      responseLatency = "$context.responseLatency"
    })
  }
}

resource "aws_apigatewayv2_api" "main" {
  name          = "rechol-api"
  description   = "Main entrypoint"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_route" "api" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "ANY /{route+}"
  target    = "integrations/${aws_apigatewayv2_integration.api.id}"
}

resource "aws_apigatewayv2_integration" "api" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_alias.backend_stable.arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_domain_name" "main" {
  domain_name = local.domain_name

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.cloudfront.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_apigatewayv2_api_mapping" "main" {
  api_id      = aws_apigatewayv2_api.main.id
  domain_name = aws_apigatewayv2_domain_name.main.id
  stage       = aws_apigatewayv2_stage.main.id
}
