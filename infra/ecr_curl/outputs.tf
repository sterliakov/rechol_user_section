data "aws_ecrpublic_authorization_token" "token" {}
data "aws_ecr_authorization_token" "token" {}

locals {
  pull_then_push_path = "${path.module}/pull_then_push.sh"
  download_dir_path   = "${path.module}/${var.name}-image"

  pull_token = (
    var.pull_ecr_is_public
    ? "Bearer ${data.aws_ecrpublic_authorization_token.token.authorization_token}"
    : "Basic ${data.aws_ecr_authorization_token.token.authorization_token}"
  )
  push_token = (
    var.push_ecr_is_public
    ? "Bearer ${data.aws_ecrpublic_authorization_token.token.authorization_token}"
    : "Basic ${data.aws_ecr_authorization_token.token.authorization_token}"
  )
}

output "command" {
  value = <<-EOF
    PULL_CURL_AUTH_HEADER='${local.pull_token}' \
      PULL_REPO_FQDN='${var.pull_repo_fqdn}' \
      PULL_REPO_NAME='${var.pull_repo_name}' \
      PULL_IMAGE_TAG='${var.pull_image_tag}' \
      PULL_DOWNLOAD_DIR_PATH='${local.download_dir_path}' \
      PUSH_CURL_AUTH_HEADER='${local.push_token}' \
      PUSH_REPO_FQDN='${var.push_repo_fqdn}' \
      PUSH_REPO_NAME='${var.push_repo_name}' \
      PUSH_IMAGE_TAG='${var.push_image_tag}' \
      '${local.pull_then_push_path}'
  EOF
}
