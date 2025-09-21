terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # Optionally configure backend here. If you didn't bootstrap the S3 backend yet,
  # leave the backend configuration to CLI with -backend-config or use local state.
  # backend "s3" {
  #   bucket         = "<your-tfstate-bucket>"
  #   key            = "polly-app/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "<your-lock-table>"
  # }
}

provider "aws" {
  region = var.aws_region
}
