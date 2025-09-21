resource "aws_sns_topic" "post_topic" {
  name = var.sns_topic_name
}
