# Import existing resources to avoid conflicts
resource "aws_dynamodb_table" "old_posts" {
  name           = "content_posts"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  
  attribute {
    name = "id"
    type = "S"
  }
  
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "old_audio" {
  bucket = "audio-storage-bucket-unique-2025"
  
  lifecycle {
    prevent_destroy = true
  }
}