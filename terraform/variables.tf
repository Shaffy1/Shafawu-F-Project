variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "mp3_bucket_name" {
  description = "S3 bucket name for audio files"
  type        = string
  default     = "audio-storage-bucket-unique-2025"
}

variable "db_table_name" {
  description = "DynamoDB table name"
  type        = string
  default     = "content_posts"
}

variable "sns_topic_name" {
  description = "SNS topic name"
  type        = string
  default     = "content-processing-topic"
}


# Optional backend variables if you use remote state:
# variable "tfstate_bucket" {
#   type    = string
#   default = ""
# }

# variable "tfstate_lock_table" {
#   type    = string
#   default = ""
# }
