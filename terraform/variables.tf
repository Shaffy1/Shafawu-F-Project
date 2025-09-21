variable "aws_region" {}

variable "mp3_bucket_name" {}

variable "db_table_name" {}

variable "sns_topic_name" {}


# Optional backend variables if you use remote state:
# variable "tfstate_bucket" {
#   type    = string
#   default = ""
# }

# variable "tfstate_lock_table" {
#   type    = string
#   default = ""
# }
