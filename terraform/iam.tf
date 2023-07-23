
resource "google_service_account" "etl" {
  account_id   = "etl-service-account"
  display_name = "ETL Service Account"
}

data "google_storage_project_service_account" "gcs" {
}

data "google_compute_default_service_account" "gce" {
}

data "google_bigquery_default_service_account" "bq" {
}

# Logs
resource "google_project_iam_member" "logwriter" {
  project = var.project_id
  role    = "roles/logging.logWriter"

  member = "serviceAccount:${google_service_account.etl.email}"
}

# Artifact Registry
resource "google_project_iam_member" "artifact_registry_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.etl.email}"
}

resource "google_project_iam_member" "gce_artifact_registry_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${data.google_compute_default_service_account.gce.email}"
}

# Cloud Storage
resource "google_project_iam_member" "cloud_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.etl.email}"
}

# BigQuery
resource "google_project_iam_member" "bigquery_data_owner" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.etl.email}"
}

resource "google_project_iam_member" "bigquery_default_data_owner" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${data.google_bigquery_default_service_account.bq.email}"
}

# Cloud Run
resource "google_project_iam_member" "cloud_run_developer" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.etl.email}"
}

# Scheduler
resource "google_project_iam_member" "cloud_scheduler_admin" {
  project = var.project_id
  role    = "roles/cloudscheduler.admin"
  member  = "serviceAccount:${google_service_account.etl.email}"
}

# Workflows
resource "google_project_iam_member" "workflows_invoker" {
  project = var.project_id
  role    = "roles/workflows.invoker"

  member = "serviceAccount:${google_service_account.etl.email}"
}

# EventArc
resource "google_project_iam_member" "eventarc_event_receiver" {
  project = var.project_id
  role    = "roles/eventarc.eventReceiver"

  member = "serviceAccount:${google_service_account.etl.email}"
}

# PubSub (For GCS CloudEvent trigger)
resource "google_project_iam_member" "pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"

  member = "serviceAccount:${data.google_storage_project_service_account.gcs.email_address}"
}
