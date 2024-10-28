# .ru domains are effectively banned by ACM as of Oct. 2024, so
# we use LetsEncrypt cert renewed via github actions.
# Thic cert s a first deployment placeholder.

resource "tls_private_key" "temporary" {
  algorithm   = "ECDSA"
  ecdsa_curve = "P256"
}

resource "tls_self_signed_cert" "temporary" {
  private_key_pem = tls_private_key.temporary.private_key_pem

  subject {
    common_name  = local.domain_name
    organization = "Project Chemistry Olympiad"
  }

  validity_period_hours = 24
  allowed_uses          = ["digital_signature"]
}

resource "aws_acm_certificate" "cloudfront" {
  private_key      = tls_private_key.temporary.private_key_pem
  certificate_body = tls_self_signed_cert.temporary.cert_pem

  lifecycle {
    ignore_changes = [private_key, certificate_body]
  }
}
