variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "agrisight-backend"
}

variable "mapbox_token_secret_id" {
  description = "Secret ID for Mapbox token"
  type        = string
  default     = "mapbox-token"
}

