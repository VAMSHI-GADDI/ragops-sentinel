output "artifact_bucket_name" {
  description = "S3 bucket used for experiment and research artifacts."
  value       = aws_s3_bucket.artifacts.bucket
}

output "ecr_repository_url" {
  description = "ECR repository URL for the RAGOps Sentinel API image."
  value       = aws_ecr_repository.api.repository_url
}

output "cloudwatch_log_group_name" {
  description = "CloudWatch log group for API logs."
  value       = aws_cloudwatch_log_group.api.name
}
