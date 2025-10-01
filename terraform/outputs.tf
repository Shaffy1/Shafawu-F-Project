output "api_base_url" {
  value = "https://${aws_cloudfront_distribution.app_distribution.domain_name}/api"
}

output "s3_bucket" {
  value = aws_s3_bucket.mp3_bucket.bucket
}

output "dynamodb_table" {
  value = aws_dynamodb_table.posts.name
}

output "cloudfront_domain" {
  value = aws_cloudfront_distribution.app_distribution.domain_name
}

output "cloudfront_url" {
  value = "https://${aws_cloudfront_distribution.app_distribution.domain_name}"
}

output "website_url" {
  value = "http://${aws_s3_bucket.website.bucket}.s3-website-${var.aws_region}.amazonaws.com"
}

output "website_bucket" {
  value = aws_s3_bucket.website.bucket
}