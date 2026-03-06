# Terraform Main Configuration
# Expected env vars: GOOGLE_CREDENTIALS (for auth)
# Testing tips: Run `terraform plan` to verify resources.

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_cloud_run_service" "backend" {
  name     = var.service_name
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/agrisight-backend:latest"
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
        env {
          name = "GEMINI_API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.gemini_api_key.secret_id
              key  = "latest"
            }
          }
        }
        env {
          name = "WEATHER_API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.weather_api_key.secret_id
              key  = "latest"
            }
          }
        }
        env {
          name = "MAPBOX_TOKEN"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.mapbox_token.secret_id
              key  = "latest"
            }
          }
        }
      }
      container_concurrency = 80
    }
  }
}

resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

resource "google_storage_bucket" "images" {
  name          = "${var.project_id}-agrisight-images"
  location      = var.region
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "weather_api_key" {
  secret_id = "weather-api-key"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "mapbox_token" {
  secret_id = var.mapbox_token_secret_id
  replication {
    auto {}
  }
}

resource "google_vertex_ai_endpoint" "agrisight_endpoint" {
  name        = "projects/${var.project_id}/locations/${var.region}/endpoints/agrisight-vertex-endpoint"
  display_name = "agrisight-vertex-endpoint"
}
