module "github_actions_cert_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-github-oidc-role"
  version = "5.47.1"

  name     = "rechol-deploy-cert"
  subjects = ["sterliakov/rechol_user_section:*"]
  policies = {
    extra = aws_iam_policy.github_actions_cert.arn
  }
}

resource "aws_iam_policy" "github_actions_cert" {
  name   = "renew-cert"
  policy = data.aws_iam_policy_document.github_actions_cert.json
}

data "aws_iam_policy_document" "github_actions_cert" {
  statement {
    effect  = "Allow"
    actions = ["acm:ImportCertificate"]
    # Apparently we can't reimport a cert with resource-specific permission?
    # https://docs.aws.amazon.com/acm/latest/userguide/authen-apipermissions.html
    resources = ["*"]
  }
}
