resource "aws_s3_bucket" "website" {
  bucket = "content-app-website-${random_string.bucket_suffix.result}"
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_website_configuration" "website" {
  bucket = aws_s3_bucket.website.id

  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "website" {
  bucket = aws_s3_bucket.website.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# Removed S3 bucket policy due to public access restrictions

resource "aws_s3_object" "index" {
  bucket       = aws_s3_bucket.website.id
  key          = "index.html"
  source       = "${path.module}/../website/index.html"
  content_type = "text/html"
  etag         = filemd5("${path.module}/../website/index.html")
}

resource "aws_s3_object" "styles" {
  bucket       = aws_s3_bucket.website.id
  key          = "styles.css"
  source       = "${path.module}/../website/styles.css"
  content_type = "text/css"
  etag         = filemd5("${path.module}/../website/styles.css")
}

resource "aws_s3_object" "scripts" {
  bucket       = aws_s3_bucket.website.id
  key          = "scripts.js"
  source       = "${path.module}/../website/scripts.js"
  content_type = "application/javascript"
  etag         = filemd5("${path.module}/../website/scripts.js")
}