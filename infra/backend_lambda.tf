data "aws_iam_policy_document" "lambda_execution_policy" {
  statement {
    actions = [
      "s3:*",
      "s3-object-lambda:*"
    ]
    resources = [
      aws_s3_bucket.private.arn,
      "${aws_s3_bucket.private.arn}/*",
      aws_s3_bucket.static.arn,
      "${aws_s3_bucket.static.arn}/*",
    ]
  }
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.backend_main.arn]
  }
  statement {
    actions   = ["ses:Get*", "ses:List*", "ses:Send*"]
    resources = ["*"]
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "rechol-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role["lambda"].json
}
resource "aws_iam_policy" "lambda_policy" {
  name   = "rechol-execution-policy"
  policy = data.aws_iam_policy_document.lambda_execution_policy.json
}
resource "aws_iam_role_policy_attachment" "be_lambda" {
  policy_arn = aws_iam_policy.lambda_policy.arn
  role       = aws_iam_role.lambda_role.name
}
resource "aws_iam_role_policy_attachment" "be_lambda_basic_managed" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

resource "aws_lambda_function" "backend_main" {
  function_name = "rechol-backend"
  role          = aws_iam_role.lambda_role.arn

  image_uri     = "${aws_ecr_repository.backend_lambda.repository_url}:${local.deployed_tag}"
  package_type  = "Image"
  architectures = ["x86_64"]
  publish       = true

  timeout     = 30
  memory_size = 512
  ephemeral_storage {
    size = 1024
  }

  environment {
    variables = {
      ENVIRONMENT = "production"
      SECRET_NAME = aws_secretsmanager_secret.backend_main.name
      SERVER_NAME = local.domain_name
    }
  }

  depends_on = [terraform_data.ecr_repo_image]
}

resource "aws_lambda_alias" "backend_stable" {
  name             = "stable"
  function_name    = aws_lambda_function.backend_main.arn
  function_version = "$LATEST"

  lifecycle {
    ignore_changes = [function_version, description]
  }
}

resource "aws_lambda_permission" "allow_cloudwatch_warmup" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.backend_main.function_name
  qualifier     = aws_lambda_alias.backend_stable.name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.warmup.arn
}

resource "aws_lambda_permission" "allow_apigw" {
  statement_id  = "AllowExecutionFromAGW"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.backend_main.function_name
  qualifier     = aws_lambda_alias.backend_stable.name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*/*"
}
