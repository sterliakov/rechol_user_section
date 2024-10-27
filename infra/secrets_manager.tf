resource "aws_secretsmanager_secret" "backend_main" {
  name                    = "backend-core"
  description             = "Core backend environment"
  recovery_window_in_days = 7
}
