#!/bin/bash
# Terraform deploy script
# Expected env vars: PROJECT_ID
# Testing tips: Run with dry-run or plan first.

set -e

if [ -z "$PROJECT_ID" ]; then
  echo "Error: PROJECT_ID environment variable is required."
  exit 1
fi

cd terraform
terraform init
terraform plan -var="project_id=$PROJECT_ID"
terraform apply -var="project_id=$PROJECT_ID" -auto-approve
