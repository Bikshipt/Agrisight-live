output "cloud_run_url" {
  value = google_cloud_run_service.backend.status[0].url
}

output "storage_bucket_name" {
  value = google_storage_bucket.images.name
}

output "vertex_ai_endpoint_name" {
  value = google_vertex_ai_endpoint.agrisight_endpoint.name
}
