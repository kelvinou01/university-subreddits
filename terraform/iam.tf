
locals {
  pubsub_service_account = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_service_account" "etl" {
  account_id   = "etl-service-account-${terraform.workspace}"
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

data "google_iam_policy" "noauth" {
  binding {
    role    = "roles/run.invoker"
    members = ["allUsers"]
  }
}

# Grant authenticated access for Cloud Scheduler
# This is safe, as only internal requests are allowed on the extract service
resource "google_cloud_run_service_iam_policy" "noauth" {
  location = google_cloud_run_v2_service.extract.location
  project  = google_cloud_run_v2_service.extract.project
  service  = google_cloud_run_v2_service.extract.name

  policy_data = data.google_iam_policy.noauth.policy_data
  depends_on  = [resource.google_cloud_run_v2_service.extract]
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

# PubSub
# Allow Cloud Storage to send object notifications
resource "google_project_iam_member" "storage_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"

  member = "serviceAccount:${data.google_storage_project_service_account.gcs.email_address}"
}

# Allow Pub/Sub to publish to dead letter queues
resource "google_project_iam_member" "pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"

  member = local.pubsub_service_account
}

resource "google_project_iam_member" "pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"

  member = local.pubsub_service_account
}
