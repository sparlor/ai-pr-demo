variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository"
  type        = string
}

variable "tf_state_bucket_name" {
  description = "S3 bucket name for Terraform state"
  type        = string
}

variable "tf_lock_table_name" {
  description = "DynamoDB table name for Terraform state lock"
  type        = string
}
