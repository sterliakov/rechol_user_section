output "github_lambda_deploy_role" {
  value = module.github_actions_deploy_lambda_role.arn
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
