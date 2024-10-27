module "github_actions_deploy_lambda_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-github-oidc-role"
  version = "5.47.1"

  subjects = ["sterliakov/rechol_user_section:*"]
  policies = {
    extra = aws_iam_policy.github_actions_deploy_lambda.arn
  }
}

resource "aws_iam_policy" "github_actions_deploy_lambda" {
  name   = "update-backend-lambda"
  policy = data.aws_iam_policy_document.github_actions_deploy_lambda.json
}

data "aws_iam_policy_document" "github_actions_deploy_lambda" {
  statement {
    effect = "Allow"
    actions = [
      "lambda:UpdateFunctionCode",
      "lambda:CreateAlias",
      "lambda:UpdateAlias",
      "lambda:InvokeFunction"
    ]
    resources = [
      aws_lambda_function.backend_main.arn,
      aws_lambda_alias.backend_stable.arn
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "s3:Get*",
      "s3:List*",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:DeleteObjectVersion",
    ]
    resources = [
      aws_s3_bucket.static.arn,
      "${aws_s3_bucket.static.arn}/*"
    ]
  }
  statement {
    effect  = "Allow"
    actions = ["acm:ImportCertiicate"]
    # Apparently we can't reimport a cert with resource-specific permission?
    # https://docs.aws.amazon.com/acm/latest/userguide/authen-apipermissions.html
    resources = ["*"]
  }
}
