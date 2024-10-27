resource "aws_ecr_repository" "backend_lambda" {
  name = "rechol-backend"
  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecr_lifecycle_policy" "remove_old_versions" {
  repository = aws_ecr_repository.backend_lambda.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 5 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 5
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

module "ecr_repo_image" {
  source = "./ecr_curl"

  name               = "rechol-backend"
  pull_ecr_is_public = true
  pull_repo_fqdn     = "public.ecr.aws"
  pull_repo_name     = "lambda/python"
  pull_image_tag     = "3.12-x86_64"
  push_ecr_is_public = false
  push_repo_fqdn     = replace(aws_ecr_repository.backend_lambda.repository_url, "//.*$/", "") # remove everything after first slash
  push_repo_name     = aws_ecr_repository.backend_lambda.name
  push_image_tag     = local.deployed_tag
}

resource "terraform_data" "ecr_repo_image" {
  triggers_replace = [
    aws_ecr_repository.backend_lambda.repository_url,
  ]

  provisioner "local-exec" {
    command = module.ecr_repo_image.command
  }
}
