resource "aws_s3_bucket" "mp3_bucket" {
  bucket        = var.mp3_bucket_name
  force_destroy = true
}

# Allow public reads of objects (your Lambda sets ACL public-read).
resource "aws_s3_bucket_public_access_block" "block" {
  bucket                  = aws_s3_bucket.mp3_bucket.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false

  depends_on = [aws_s3_bucket.mp3_bucket]
}

resource "aws_s3_bucket_policy" "public_policy" {
  bucket = aws_s3_bucket.mp3_bucket.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "PublicReadGetObject",
        Effect    = "Allow",
        Principal = "*",
        Action    = "s3:GetObject",
        Resource  = "${aws_s3_bucket.mp3_bucket.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.block]
}
