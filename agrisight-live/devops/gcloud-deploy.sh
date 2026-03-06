#!/bin/bash
# GCloud deploy script
# Expected env vars: PROJECT_ID, REGION
# Testing tips: Ensure gcloud is authenticated.

set -e

PROJECT_ID=${PROJECT_ID:-"my-gcp-project"}
REGION=${REGION:-"us-central1"}

echo "Deploying to project $PROJECT_ID in region $REGION..."

gcloud builds submit --config cloudbuild.yaml --substitutions=_REGION=$REGION .
