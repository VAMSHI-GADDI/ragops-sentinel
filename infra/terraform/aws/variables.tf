variable "aws_region" {
  description = "AWS region for RAGOps Sentinel infrastructure."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix for resources."
  type        = string
  default     = "ragops-sentinel"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "artifact_bucket_force_destroy" {
  description = "Whether to force destroy the artifact bucket in non-production environments."
  type        = bool
  default     = false
}

variable "container_image_tag_mutability" {
  description = "ECR tag mutability setting."
  type        = string
  default     = "MUTABLE"

  validation {
    condition     = contains(["MUTABLE", "IMMUTABLE"], var.container_image_tag_mutability)
    error_message = "container_image_tag_mutability must be MUTABLE or IMMUTABLE."
  }
}
