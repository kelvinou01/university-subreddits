# Ref: https://cloud.google.com/run/docs/execute/jobs-on-schedule#terraform
resource "google_cloud_scheduler_job" "extract_scheduler" {
  name        = "extract-scheduler"
  description = "Scheduler to trigger the extract function"

  schedule  = "0 18 * * *"
  time_zone = "Asia/Singapore"

  http_target {
    http_method = "POST"
    uri         = "https://${google_cloud_run_v2_job.extract.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.extract.name}:run"

    oauth_token {
      service_account_email = google_service_account.etl.email
    }
  }

  depends_on = [
    resource.google_cloud_run_v2_job.extract,
  ]
}
