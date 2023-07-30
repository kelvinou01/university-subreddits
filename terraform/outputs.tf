
output "extract_image" {
  value = format(
    "%s-docker.pkg.dev/%s/%s/extract@%s",
    var.region, var.project_id, var.docker_repo_id, var.extract_image_digest
  )
}

output "transform_image" {
  value = format(
    "%s-docker.pkg.dev/%s/%s/transform@%s",
    var.region, var.project_id, var.docker_repo_id, var.transform_image_digest
  )
}

output "load_image" {
  value = format(
    "%s-docker.pkg.dev/%s/%s/load@%s",
    var.region, var.project_id, var.docker_repo_id, var.load_image_digest
  )
}

output "extract_uri" {
  value = google_cloud_run_v2_service.extract.uri
}

output "transform_uri" {
  value = google_cloud_run_v2_service.transform.uri
}

output "load_uri" {
  value = google_cloud_run_v2_service.load.uri
}
