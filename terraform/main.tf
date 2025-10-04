terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "random_id" "suffix" {
  byte_length = 4
}

# Website S3 Bucket
resource "aws_s3_bucket" "website" {
  bucket = "polly-website-${random_id.suffix.hex}"
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

# Upload website files
resource "aws_s3_object" "website_files" {
  for_each = {
    "index.html" = "text/html"
    "styles.css" = "text/css"
    "scripts.js" = "application/javascript"
  }
  bucket       = aws_s3_bucket.website.id
  key          = each.key
  source       = "${path.module}/../website/${each.key}"
  content_type = each.value
  etag         = filemd5("${path.module}/../website/${each.key}")
}

# CloudFront
resource "aws_cloudfront_distribution" "website" {
  origin {
    domain_name = aws_s3_bucket_website_configuration.website.website_endpoint
    origin_id   = "S3-Website"
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }
  enabled             = true
  default_root_object = "index.html"
  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-Website"
    viewer_protocol_policy = "redirect-to-https"
    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }
  }
  restrictions {
    geo_restriction { restriction_type = "none" }
  }
  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

data "aws_caller_identity" "current" {}

# Outputs
output "website_url" {
  value = "https://${aws_cloudfront_distribution.website.domain_name}"
}

output "website_bucket" {
  value = aws_s3_bucket.website.bucket
}

output "api_url" {
  value = "https://q7dnar5wh8.execute-api.us-east-1.amazonaws.com/prod"
}