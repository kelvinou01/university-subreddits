resource "google_eventarc_trigger" "trigger_workflow" {
  name     = "trigger-workflow"
  location = var.region
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.storage.object.v1.finalized"
  }
  matching_criteria {
    attribute = "bucket"
    value     = google_storage_bucket.etl_bucket.name
  }
  destination {
    workflow = google_workflows_workflow.run_next_job.id
  }

  service_account = google_service_account.etl.email
  depends_on = [
    resource.google_project_iam_member.eventarc_event_receiver,
    resource.google_project_iam_member.pubsub_publisher
  ]
}
