resource "google_eventarc_trigger" "trigger_transform" {
  name     = "trigger-transform"
  location = var.region
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.storage.object.v1.finalized"
  }
  matching_criteria {
    attribute = "bucket"
    value     = google_storage_bucket.raw_data_bucket.name
  }

  destination {
    cloud_run_service {
      service = google_cloud_run_v2_service.transform.name
      region  = google_cloud_run_v2_service.transform.location
    }
  }

  service_account = google_service_account.etl.email
  depends_on = [
    resource.google_project_iam_member.eventarc_event_receiver,
    resource.google_project_iam_member.pubsub_publisher
  ]
}

resource "google_eventarc_trigger" "trigger_load" {
  name     = "trigger-load"
  location = var.region
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.storage.object.v1.finalized"
  }
  matching_criteria {
    attribute = "bucket"
    value     = google_storage_bucket.transformed_data_bucket.name
  }

  destination {
    cloud_run_service {
      service = google_cloud_run_v2_service.load.name
      region  = google_cloud_run_v2_service.load.location
    }
  }

  service_account = google_service_account.etl.email
  depends_on = [
    resource.google_project_iam_member.eventarc_event_receiver,
    resource.google_project_iam_member.pubsub_publisher
  ]
}
