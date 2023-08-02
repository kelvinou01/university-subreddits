
resource "google_storage_notification" "raw_data" {
  bucket         = google_storage_bucket.raw_data_bucket.name
  payload_format = "JSON_API_V1"
  topic          = google_pubsub_topic.transform.id
  event_types    = ["OBJECT_FINALIZE"]

  depends_on = [google_project_iam_member.pubsub_publisher]
}

resource "google_storage_notification" "transformed_data" {
  bucket         = google_storage_bucket.transformed_data_bucket.name
  payload_format = "JSON_API_V1"
  topic          = google_pubsub_topic.load.id
  event_types    = ["OBJECT_FINALIZE"]

  depends_on = [google_project_iam_member.pubsub_publisher]
}

resource "google_pubsub_topic" "transform" {
  name = "transform"
}

resource "google_pubsub_topic" "load" {
  name = "load"
}

resource "google_pubsub_subscription" "transform" {
  name  = "transform"
  topic = google_pubsub_topic.transform.name

  ack_deadline_seconds = 600

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.transform_dead_letter.id
    max_delivery_attempts = 5
  }

  push_config {
    push_endpoint = google_cloud_run_v2_service.transform.uri
    oidc_token {
      service_account_email = google_service_account.etl.email
    }
    attributes = {
      x-goog-version = "v1"
    }
  }

  retry_policy {
    minimum_backoff = "60s"
  }
}

resource "google_pubsub_subscription" "load" {
  name  = "load"
  topic = google_pubsub_topic.load.name

  ack_deadline_seconds = 600

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.load_dead_letter.id
    max_delivery_attempts = 5
  }

  push_config {
    push_endpoint = google_cloud_run_v2_service.load.uri
    oidc_token {
      service_account_email = google_service_account.etl.email
    }
    attributes = {
      x-goog-version = "v1"
    }
  }

  retry_policy {
    minimum_backoff = "60s"
  }
}

resource "google_pubsub_topic" "transform_dead_letter" {
  name                       = "transform-dead-letter"
  message_retention_duration = "600s"
}

resource "google_pubsub_topic" "load_dead_letter" {
  name                       = "load-dead-letter"
  message_retention_duration = "600s"
}
