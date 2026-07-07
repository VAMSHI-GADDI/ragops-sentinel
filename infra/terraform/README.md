# RAGOps Sentinel Terraform Templates

## Purpose

This folder contains Terraform templates for cloud infrastructure that can support RAGOps Sentinel deployment workflows.

## Included Resources

- S3 bucket for experiment/research artifacts
- S3 versioning
- S3 server-side encryption
- ECR repository for API container images
- ECR image scan-on-push
- CloudWatch log group for API logs

## Usage

From this folder:

terraform init
terraform plan -var-file=terraform.tfvars.example

## Honest Limitation

These are infrastructure-as-code templates. They do not claim that RAGOps Sentinel is live-deployed on AWS unless terraform apply is actually run and validated.
