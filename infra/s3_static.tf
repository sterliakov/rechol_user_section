resource "aws_s3_bucket" "static" {
  bucket = "rechol-static"
}

resource "aws_s3_bucket_public_access_block" "static" {
  bucket = aws_s3_bucket.static.id

  block_public_acls       = true
  block_public_policy     = false
  ignore_public_acls      = true
  restrict_public_buckets = false
}

resource "aws_s3_bucket_server_side_encryption_configuration" "static" {
  bucket = aws_s3_bucket.static.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

data "aws_iam_policy_document" "allow_access_from_cloudfront" {
  statement {
    # TODO: proxy this through CloudFront
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    sid     = "AllowPublicStaticRead"
    actions = ["s3:GetObject"]
    resources = [
      "${aws_s3_bucket.static.arn}/static/*",
    ]
  }

  # statement {
  #   actions = ["s3:GetObject"]
  #   principals {
  #     type        = "Service"
  #     identifiers = ["cloudfront.amazonaws.com"]
  #   }
  #   resources = ["arn:aws:s3:::${aws_s3_bucket.static.bucket}/*"]
  #   condition {
  #     test     = "StringEquals"
  #     variable = "AWS:SourceArn"
  #     values   = [aws_cloudfront_distribution.main.arn]
  #   }
  # }
}

resource "aws_s3_bucket_policy" "allow_access_from_cloudfront" {
  bucket = aws_s3_bucket.static.id
  policy = data.aws_iam_policy_document.allow_access_from_cloudfront.json
}

resource "aws_s3_bucket_cors_configuration" "allow_access_from_everywhere" {
  bucket = aws_s3_bucket.static.id

  cors_rule {
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
  }
}
