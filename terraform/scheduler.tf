# Ref: https://cloud.google.com/run/docs/execute/jobs-on-schedule#terraform
resource "google_cloud_scheduler_job" "extract_scheduler" {
  name        = "extract-scheduler"
  description = "Scheduler to trigger the extract function"

  schedule  = "0 18 * * *"
  time_zone = "Asia/Singapore"

  http_target {
    http_method = "GET"
    uri         = google_cloud_run_v2_service.extract.uri
  }

  depends_on = [
    resource.google_cloud_run_v2_service.extract,
  ]
}
