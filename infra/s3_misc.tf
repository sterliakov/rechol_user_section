resource "aws_s3_bucket" "misc" {
  bucket = "rechol-misc"
}

resource "aws_s3_bucket_versioning" "misc" {
  bucket = aws_s3_bucket.misc.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "misc" {
  bucket = aws_s3_bucket.misc.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "misc" {
  bucket = aws_s3_bucket.misc.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
