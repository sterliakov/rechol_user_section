output "github_lambda_deploy_role" {
  value = module.github_actions_deploy_lambda_role.arn
}
output "github_cert_deploy_role" {
  value = module.github_actions_cert_role.arn
}

output "backend_lambda_ecr_url" {
  value = aws_ecr_repository.backend_lambda.repository_url
}
output "backend_lambda_deployed_tag" {
  value = local.deployed_tag
}

output "ssl_certificate_arn" {
  value = aws_acm_certificate.cloudfront.arn
}
output "api_gateway_fqdn" {
  value = aws_apigatewayv2_domain_name.main.domain_name_configuration[0].target_domain_name
}
